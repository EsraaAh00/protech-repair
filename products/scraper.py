"""
LiftMaster Product Scraper
يقوم بجلب المنتجات من موقع LiftMaster وحفظها في قاعدة البيانات
"""
import requests
from bs4 import BeautifulSoup
from django.core.files.base import ContentFile
from django.utils.text import slugify
from django.db import transaction
from .models import Product, ProductCategory, ProductImage
import logging
import time
from urllib.parse import urljoin
import re

logger = logging.getLogger(__name__)


class LiftMasterScraper:
    """
    Class to scrape products from LiftMaster website
    """
    BASE_URL = "https://www.liftmaster-me.com"
    PRODUCTS_URL = "https://www.liftmaster-me.com/products/"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.scraped_count = 0
        self.skipped_count = 0
        self.error_count = 0
    
    def get_or_create_category(self, category_name):
        """
        Get or create product category
        """
        if not category_name:
            category_name = "Garage Door Openers"
        
        category, created = ProductCategory.objects.get_or_create(
            name_en=category_name,
            defaults={
                'name': category_name,
                'slug': slugify(category_name),
                'is_active': True,
            }
        )
        return category
    
    def download_image(self, image_url):
        """
        Download image from URL and return ContentFile
        """
        try:
            # Skip data URLs (SVG placeholders)
            if image_url.startswith('data:'):
                logger.debug(f"Skipping data URL (placeholder image)")
                return None
            
            if not image_url.startswith('http'):
                image_url = urljoin(self.BASE_URL, image_url)
            
            response = self.session.get(image_url, timeout=30)
            if response.status_code == 200:
                # Check if content is actually an image
                content_type = response.headers.get('content-type', '').lower()
                if not any(img_type in content_type for img_type in ['image/', 'octet-stream']):
                    logger.debug(f"Skipping non-image content: {content_type}")
                    return None
                
                # Get filename from URL or generate one
                filename = image_url.split('/')[-1].split('?')[0]
                if not filename or len(filename) < 3:
                    filename = f"liftmaster_{int(time.time())}.jpg"
                
                return ContentFile(response.content, name=filename)
        except Exception as e:
            logger.error(f"Error downloading image {image_url}: {e}")
        return None
    
    def extract_model_number(self, title):
        """
        Extract model number from product title
        """
        # Common patterns for LiftMaster model numbers
        patterns = [
            r'LM[A-Z0-9\-]+',
            r'\d{4,5}[A-Z]*',
            r'Model\s+([A-Z0-9\-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                return match.group(0) if 'Model' not in pattern else match.group(1)
        return None
    
    def scrape_product_detail(self, product_url):
        """
        Scrape detailed information from a product page
        """
        try:
            response = self.session.get(product_url, timeout=30)
            if response.status_code != 200:
                logger.error(f"Failed to fetch product page: {product_url}")
                return None
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Extract product information
            product_data = {
                'url': product_url,
                'all_images': []  # List to store all images
            }
            
            # Title
            title_elem = soup.find('h1') or soup.find('h2', class_='product-title')
            if title_elem:
                product_data['title'] = title_elem.get_text(strip=True)
            
            # Description
            desc_elem = soup.find('div', class_='product-description') or soup.find('div', class_='description')
            if desc_elem:
                product_data['description'] = desc_elem.get_text(strip=True)
            
            # Collect ALL images from the page
            all_images_found = set()  # Use set to avoid duplicates
            
            # Strategy 1: Look for product gallery/slider
            gallery_elem = soup.find('div', class_=re.compile(r'gallery|slider|carousel|images', re.IGNORECASE))
            if gallery_elem:
                for img in gallery_elem.find_all('img'):
                    # Try multiple attributes for lazy-loaded images
                    img_src = (img.get('data-src') or 
                              img.get('data-lazy-src') or 
                              img.get('data-original') or 
                              img.get('data-lazy') or
                              img.get('src', ''))
                    
                    # Skip data URLs and placeholders
                    if img_src and not img_src.startswith('data:'):
                        if not any(skip in img_src.lower() for skip in ['logo', 'icon', 'favicon', 'placeholder', 'svg']):
                            all_images_found.add(img_src)
            
            # Strategy 2: Look for product-related images
            product_section = soup.find('div', class_=re.compile(r'product|item-detail|single-product', re.IGNORECASE))
            if product_section:
                for img in product_section.find_all('img'):
                    img_src = (img.get('data-src') or 
                              img.get('data-lazy-src') or 
                              img.get('data-original') or 
                              img.get('data-lazy') or
                              img.get('src', ''))
                    
                    if img_src and not img_src.startswith('data:'):
                        if not any(skip in img_src.lower() for skip in ['logo', 'icon', 'favicon', 'placeholder', 'button', 'svg']):
                            all_images_found.add(img_src)
            
            # Strategy 3: Main product image
            img_elem = soup.find('img', class_='product-image') or soup.find('div', class_='product-gallery')
            if img_elem:
                if img_elem.name == 'img':
                    img_src = (img_elem.get('data-src') or 
                              img_elem.get('data-lazy-src') or 
                              img_elem.get('data-original') or
                              img_elem.get('src', ''))
                    
                    if img_src and not img_src.startswith('data:'):
                        all_images_found.add(img_src)
                        product_data['image_url'] = img_src  # Main image
                else:
                    img = img_elem.find('img')
                    if img:
                        img_src = (img.get('data-src') or 
                                  img.get('data-lazy-src') or 
                                  img.get('data-original') or
                                  img.get('src', ''))
                        
                        if img_src and not img_src.startswith('data:'):
                            all_images_found.add(img_src)
                            product_data['image_url'] = img_src
            
            # Strategy 4: Look for thumbnail images (often in galleries)
            thumbnails = soup.find_all('img', class_=re.compile(r'thumb|small|preview', re.IGNORECASE))
            for thumb in thumbnails:
                # Try to get the full-size version
                img_src = (thumb.get('data-full') or 
                          thumb.get('data-large') or 
                          thumb.get('data-src') or 
                          thumb.get('data-original') or
                          thumb.get('src', ''))
                
                if img_src and not img_src.startswith('data:'):
                    if not any(skip in img_src.lower() for skip in ['logo', 'icon', 'favicon', 'svg']):
                        all_images_found.add(img_src)
            
            # Convert set to list and store all images
            product_data['all_images'] = list(all_images_found)
            logger.info(f"Found {len(all_images_found)} images for product")
            
            # If no main image set but we have images, use the first one as main
            if not product_data.get('image_url') and product_data['all_images']:
                product_data['image_url'] = product_data['all_images'][0]
            
            # PDF link
            pdf_link = soup.find('a', href=re.compile(r'\.pdf$', re.IGNORECASE))
            if pdf_link:
                pdf_url = pdf_link.get('href', '')
                if not pdf_url.startswith('http'):
                    pdf_url = urljoin(self.BASE_URL, pdf_url)
                product_data['pdf_url'] = pdf_url
            
            # Features
            features = []
            features_section = soup.find('ul', class_='features') or soup.find('div', class_='features')
            if features_section:
                for li in features_section.find_all('li'):
                    features.append(li.get_text(strip=True))
            product_data['features'] = '\n'.join(features) if features else ''
            
            # Category
            category_elem = soup.find('span', class_='category') or soup.find('a', class_='category')
            if category_elem:
                product_data['category'] = category_elem.get_text(strip=True)
            
            return product_data
            
        except Exception as e:
            logger.error(f"Error scraping product detail {product_url}: {e}")
            return None
    
    def scrape_products_list(self):
        """
        Scrape products from the main products page
        """
        try:
            # First, try the main products page
            logger.info(f"Fetching products from: {self.PRODUCTS_URL}")
            response = self.session.get(self.PRODUCTS_URL, timeout=30)
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch products page: {response.status_code}")
                # Try the home page as fallback
                logger.info(f"Trying home page: {self.BASE_URL}")
                response = self.session.get(self.BASE_URL, timeout=30)
                if response.status_code != 200:
                    logger.error(f"Failed to fetch home page: {response.status_code}")
                    return []
            
            soup = BeautifulSoup(response.content, 'lxml')
            logger.info(f"Page title: {soup.title.string if soup.title else 'No title'}")
            
            products = []
            
            # Try multiple strategies to find products
            # Strategy 1: Look for product cards/items with various class names
            product_elements = []
            
            # Common class patterns
            class_patterns = [
                'product-item', 'product-card', 'product', 'item',
                'post', 'entry', 'article', 'box'
            ]
            
            for pattern in class_patterns:
                elements = soup.find_all(['div', 'article', 'section'], class_=re.compile(pattern, re.IGNORECASE))
                if elements:
                    logger.info(f"Found {len(elements)} elements with class pattern '{pattern}'")
                    product_elements.extend(elements)
                    break  # Use the first pattern that finds results
            
            # Strategy 2: Look for links that might be products
            if not product_elements:
                logger.info("No product cards found, looking for product links...")
                # Look for links in the main content area
                main_content = soup.find(['main', 'div'], id=re.compile(r'content|main', re.IGNORECASE))
                if not main_content:
                    main_content = soup.find(['div'], class_=re.compile(r'content|main|products', re.IGNORECASE))
                
                if main_content:
                    # Find all links that might be products
                    all_links = main_content.find_all('a', href=True)
                    logger.info(f"Found {len(all_links)} links in main content")
                    
                    # Filter links that look like product pages
                    for link in all_links:
                        href = link.get('href', '')
                        # Look for patterns in URLs
                        if any(keyword in href.lower() for keyword in ['product', 'lm', 'opener', 'door', 'garage']):
                            # Check if link has an image (likely a product)
                            img = link.find('img') or link.find_parent(['div', 'article']).find('img') if link.find_parent(['div', 'article']) else None
                            if img or link.get_text(strip=True):
                                product_elements.append(link)
            
            # Strategy 3: Look for h2/h3 with links (common structure)
            if not product_elements:
                logger.info("Looking for heading-based products...")
                headings = soup.find_all(['h2', 'h3', 'h4'])
                for heading in headings:
                    link = heading.find('a', href=True)
                    if link:
                        product_elements.append(heading)
            
            logger.info(f"Total potential product elements found: {len(product_elements)}")
            
            # Process each element
            for element in product_elements:
                try:
                    product_info = {}
                    
                    # Get product link
                    if element.name == 'a':
                        link = element
                    else:
                        link = element.find('a', href=True)
                    
                    if not link:
                        continue
                    
                    product_url = link.get('href', '')
                    if not product_url:
                        continue
                        
                    # Skip non-product links
                    if any(skip in product_url.lower() for skip in ['#', 'javascript:', 'mailto:', 'tel:']):
                        continue
                    
                    if not product_url.startswith('http'):
                        product_url = urljoin(self.BASE_URL, product_url)
                    
                    product_info['url'] = product_url
                    
                    # Get title from link or element
                    title_elem = (element.find(['h2', 'h3', 'h4']) or 
                                 link.find(['h2', 'h3', 'h4']) or 
                                 link)
                    
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        # Clean up title
                        title = re.sub(r'\s+', ' ', title)
                        if title and len(title) > 3:  # Meaningful title
                            product_info['title'] = title
                    
                    # Get all images for this product
                    product_images = []
                    
                    # Get main image
                    img = element.find('img')
                    if not img and element.name == 'a':
                        parent = element.find_parent(['div', 'article'])
                        if parent:
                            img = parent.find('img')
                    
                    if img:
                        img_src = (img.get('data-src') or 
                                  img.get('data-lazy-src') or 
                                  img.get('data-original') or
                                  img.get('src', ''))
                        
                        if img_src and not img_src.startswith('data:'):
                            product_info['image_url'] = img_src
                            product_images.append(img_src)
                    
                    # Try to find additional images in the element
                    all_imgs = element.find_all('img') if element.name != 'img' else [element]
                    for img_elem in all_imgs:
                        img_src = (img_elem.get('data-src') or 
                                  img_elem.get('data-lazy-src') or 
                                  img_elem.get('data-original') or
                                  img_elem.get('src', ''))
                        
                        if img_src and not img_src.startswith('data:'):
                            if img_src not in product_images:
                                if not any(skip in img_src.lower() for skip in ['logo', 'icon', 'favicon', 'button', 'svg']):
                                    product_images.append(img_src)
                    
                    # Store all images (only real image URLs, not data URLs)
                    if product_images:
                        product_info['all_images'] = product_images
                    
                    # Get short description if available
                    desc_elem = (element.find('p') or 
                                element.find('div', class_=re.compile(r'desc|excerpt', re.IGNORECASE)))
                    if desc_elem:
                        desc = desc_elem.get_text(strip=True)
                        if desc and len(desc) > 10:
                            product_info['short_description'] = desc[:300]
                    
                    # Only add if we have at least a title
                    if product_info.get('title'):
                        # Avoid duplicates
                        if not any(p.get('url') == product_url for p in products):
                            products.append(product_info)
                            logger.info(f"Found product: {product_info['title'][:50]}")
                        
                except Exception as e:
                    logger.error(f"Error parsing product element: {e}")
                    continue
            
            logger.info(f"Successfully extracted {len(products)} products")
            return products
            
        except Exception as e:
            logger.error(f"Error scraping products list: {e}", exc_info=True)
            return []
    
    @transaction.atomic
    def save_product(self, product_data):
        """
        Save scraped product to database with all images
        """
        try:
            # Extract model number
            title = product_data.get('title', '')
            model_number = self.extract_model_number(title)
            
            # Check if product already exists
            if model_number:
                existing = Product.objects.filter(model_number=model_number).first()
                if existing:
                    logger.info(f"Product {model_number} already exists, skipping...")
                    self.skipped_count += 1
                    return existing
            else:
                # If no model number, check by name
                existing = Product.objects.filter(name_en=title).first()
                if existing:
                    logger.info(f"Product '{title}' already exists, skipping...")
                    self.skipped_count += 1
                    return existing
            
            # Get or create category
            category_name = product_data.get('category', 'Garage Door Openers')
            category = self.get_or_create_category(category_name)
            
            # Create product
            product = Product(
                name=title,
                name_en=title,
                slug=slugify(title),
                model_number=model_number or '',
                category=category,
                product_type='opener',
                brand='LiftMaster',
                short_description=product_data.get('short_description', '')[:300],
                description=product_data.get('description', title),
                features=product_data.get('features', ''),
                pdf_url=product_data.get('pdf_url', ''),
                is_active=True,
            )
            
            # Download and save main image
            main_image_url = product_data.get('image_url', '')
            if main_image_url:
                image_file = self.download_image(main_image_url)
                if image_file:
                    product.image = image_file
                    logger.info(f"  ✓ Downloaded main image")
            
            product.save()
            logger.info(f"Successfully saved product: {title}")
            
            # Download and save all additional images
            all_images = product_data.get('all_images', [])
            if all_images:
                logger.info(f"  Downloading {len(all_images)} images...")
                saved_images_count = 0
                
                for idx, img_url in enumerate(all_images):
                    try:
                        # Skip if it's the same as main image (already saved)
                        if img_url == main_image_url:
                            continue
                        
                        # Download image
                        image_file = self.download_image(img_url)
                        if image_file:
                            # Create ProductImage instance
                            product_image = ProductImage(
                                product=product,
                                image=image_file,
                                is_main=(idx == 0 and not main_image_url),
                                order=idx
                            )
                            product_image.save()
                            saved_images_count += 1
                            logger.info(f"  ✓ Saved image {saved_images_count}/{len(all_images)}")
                        
                        # Small delay between image downloads
                        time.sleep(0.5)
                        
                    except Exception as img_error:
                        logger.warning(f"  ✗ Failed to save image {idx + 1}: {img_error}")
                        continue
                
                logger.info(f"  Total images saved: {saved_images_count} additional images")
            
            self.scraped_count += 1
            return product
            
        except Exception as e:
            logger.error(f"Error saving product: {e}")
            self.error_count += 1
            return None
    
    def scrape_all(self, fetch_details=False):
        """
        Main method to scrape all products
        
        Args:
            fetch_details: If True, fetch detailed information for each product (slower)
        """
        logger.info("Starting LiftMaster product scraping...")
        
        # Reset counters
        self.scraped_count = 0
        self.skipped_count = 0
        self.error_count = 0
        
        # Get products list
        products = self.scrape_products_list()
        
        if not products:
            logger.warning("No products found on the products page")
            return {
                'success': False,
                'message': 'No products found',
                'scraped': 0,
                'skipped': 0,
                'errors': 0
            }
        
        logger.info(f"Found {len(products)} products to process")
        
        # Process each product
        for product_data in products:
            try:
                # Fetch detailed information if requested
                if fetch_details:
                    detailed_data = self.scrape_product_detail(product_data['url'])
                    if detailed_data:
                        # Merge all_images lists (avoid duplicates)
                        existing_images = set(product_data.get('all_images', []))
                        new_images = set(detailed_data.get('all_images', []))
                        all_combined_images = list(existing_images | new_images)
                        
                        product_data.update(detailed_data)
                        product_data['all_images'] = all_combined_images
                
                # Save product
                self.save_product(product_data)
                
                # Be nice to the server
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error processing product: {e}")
                self.error_count += 1
                continue
        
        logger.info(f"Scraping completed. Scraped: {self.scraped_count}, Skipped: {self.skipped_count}, Errors: {self.error_count}")
        
        return {
            'success': True,
            'message': f'Successfully scraped {self.scraped_count} products',
            'scraped': self.scraped_count,
            'skipped': self.skipped_count,
            'errors': self.error_count
        }


def scrape_liftmaster_products(fetch_details=False):
    """
    Convenience function to scrape LiftMaster products
    """
    scraper = LiftMasterScraper()
    return scraper.scrape_all(fetch_details=fetch_details)

