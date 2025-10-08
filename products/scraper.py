"""
LiftMaster Product Scraper
يقوم بجلب المنتجات من موقع LiftMaster وحفظها في قاعدة البيانات
"""
import requests
from bs4 import BeautifulSoup
from django.core.files.base import ContentFile
from django.utils.text import slugify
from django.db import transaction
from .models import Product, ProductCategory
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
            if not image_url.startswith('http'):
                image_url = urljoin(self.BASE_URL, image_url)
            
            response = self.session.get(image_url, timeout=30)
            if response.status_code == 200:
                # Get filename from URL or generate one
                filename = image_url.split('/')[-1]
                if not filename or '?' in filename:
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
            }
            
            # Title
            title_elem = soup.find('h1') or soup.find('h2', class_='product-title')
            if title_elem:
                product_data['title'] = title_elem.get_text(strip=True)
            
            # Description
            desc_elem = soup.find('div', class_='product-description') or soup.find('div', class_='description')
            if desc_elem:
                product_data['description'] = desc_elem.get_text(strip=True)
            
            # Main image
            img_elem = soup.find('img', class_='product-image') or soup.find('div', class_='product-gallery')
            if img_elem:
                if img_elem.name == 'img':
                    product_data['image_url'] = img_elem.get('src', '')
                else:
                    img = img_elem.find('img')
                    if img:
                        product_data['image_url'] = img.get('src', '')
            
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
                    
                    # Get image
                    img = element.find('img')
                    if not img and element.name == 'a':
                        parent = element.find_parent(['div', 'article'])
                        if parent:
                            img = parent.find('img')
                    
                    if img:
                        img_src = img.get('src', '') or img.get('data-src', '')
                        if img_src:
                            product_info['image_url'] = img_src
                    
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
        Save scraped product to database
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
            
            # Download and save image
            image_url = product_data.get('image_url', '')
            if image_url:
                image_file = self.download_image(image_url)
                if image_file:
                    product.image = image_file
            
            product.save()
            
            logger.info(f"Successfully saved product: {title}")
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
                        product_data.update(detailed_data)
                
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

