"""
Enhanced scraper using Selenium to fetch all products from LiftMaster website
يجلب جميع المنتجات من موقع LiftMaster باستخدام Selenium
"""
import logging
import time
import re
from urllib.parse import urljoin
from django.core.files.base import ContentFile
from django.utils.text import slugify
from django.db import transaction

logger = logging.getLogger(__name__)

# Try to import Selenium
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    logger.warning("Selenium not available. Install with: pip install selenium webdriver-manager")

import requests


class EnhancedLiftMasterScraper:
    """
    Enhanced scraper that fetches all products from LiftMaster website
    """
    BASE_URL = "https://www.liftmaster-me.com"
    PRODUCTS_URL = "https://www.liftmaster-me.com/products/"
    
    def __init__(self):
        self.scraped_count = 0
        self.skipped_count = 0
        self.error_count = 0
        self.driver = None
    
    def setup_driver(self):
        """Setup Selenium WebDriver with proper options"""
        try:
            chrome_options = Options()
            
            # Basic options
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            
            # Add experimental options to avoid detection
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Try to initialize WebDriver
            logger.info("Installing/updating ChromeDriver...")
            service = Service(ChromeDriverManager().install())
            
            logger.info("Initializing Chrome WebDriver...")
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Execute CDP commands to avoid detection
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            logger.info("Chrome WebDriver initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize WebDriver: {e}")
            logger.error("Make sure Chrome browser is installed on your system")
            logger.error("If the error persists, try: pip install --upgrade selenium webdriver-manager")
            return False
    
    def close_driver(self):
        """Close the WebDriver"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("WebDriver closed")
            except Exception as e:
                logger.error(f"Error closing WebDriver: {e}")
    
    def download_image(self, image_url):
        """Download image from URL"""
        try:
            if not image_url.startswith('http'):
                image_url = urljoin(self.BASE_URL, image_url)
            
            response = requests.get(image_url, timeout=30)
            if response.status_code == 200:
                filename = image_url.split('/')[-1].split('?')[0]
                if not filename or len(filename) < 3:
                    filename = f"liftmaster_{int(time.time())}.jpg"
                
                return ContentFile(response.content, name=filename)
        except Exception as e:
            logger.error(f"Error downloading image {image_url}: {e}")
        return None
    
    def extract_model_number(self, title):
        """Extract model number from product title"""
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
    
    def scrape_all_products(self, fetch_details=False):
        """
        Scrape all products from LiftMaster website using Selenium
        """
        from .models import Product, ProductCategory
        
        if not SELENIUM_AVAILABLE:
            return {
                'success': False,
                'message': 'Selenium not available. Install with: pip install selenium webdriver-manager',
                'scraped': 0,
                'skipped': 0,
                'errors': 0
            }
        
        # Setup driver
        if not self.setup_driver():
            return {
                'success': False,
                'message': 'Failed to initialize WebDriver',
                'scraped': 0,
                'skipped': 0,
                'errors': 0
            }
        
        try:
            logger.info(f"Fetching products from: {self.PRODUCTS_URL}")
            
            # Navigate to products page
            self.driver.get(self.PRODUCTS_URL)
            
            # Wait for page to load
            time.sleep(3)
            
            # Try to find product elements
            products = []
            
            # Strategy 1: Look for links with product patterns
            try:
                # Wait for any product links to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Get all links
                all_links = self.driver.find_elements(By.TAG_NAME, "a")
                
                for link in all_links:
                    try:
                        href = link.get_attribute('href')
                        text = link.text.strip()
                        
                        # Check if it looks like a product link
                        if href and text and any(keyword in href.lower() for keyword in ['product', 'lm', 'opener', 'door']):
                            # Try to find an image near this link
                            try:
                                parent = link.find_element(By.XPATH, '..')
                                img = parent.find_element(By.TAG_NAME, 'img')
                                img_src = img.get_attribute('src')
                            except:
                                img_src = None
                            
                            if text and len(text) > 3:
                                products.append({
                                    'url': href,
                                    'title': text,
                                    'image_url': img_src
                                })
                                logger.info(f"Found product: {text[:50]}")
                    except Exception as e:
                        continue
                
            except Exception as e:
                logger.error(f"Error finding products: {e}")
            
            # Remove duplicates
            unique_products = []
            seen_urls = set()
            for product in products:
                if product['url'] not in seen_urls:
                    unique_products.append(product)
                    seen_urls.add(product['url'])
            
            logger.info(f"Found {len(unique_products)} unique products")
            
            if not unique_products:
                # If no products found, try home page
                logger.info("No products found on products page, trying home page...")
                self.driver.get(self.BASE_URL)
                time.sleep(3)
                
                # Repeat search on home page
                all_links = self.driver.find_elements(By.TAG_NAME, "a")
                for link in all_links:
                    try:
                        href = link.get_attribute('href')
                        text = link.text.strip()
                        
                        if href and text and 'lm' in text.lower():
                            try:
                                parent = link.find_element(By.XPATH, '..')
                                img = parent.find_element(By.TAG_NAME, 'img')
                                img_src = img.get_attribute('src')
                            except:
                                img_src = None
                            
                            if text and len(text) > 3 and href not in seen_urls:
                                unique_products.append({
                                    'url': href,
                                    'title': text,
                                    'image_url': img_src
                                })
                                seen_urls.add(href)
                                logger.info(f"Found product on home: {text[:50]}")
                    except:
                        continue
            
            logger.info(f"Total products to process: {len(unique_products)}")
            
            # Get or create category
            category, _ = ProductCategory.objects.get_or_create(
                name_en='Garage Door Openers',
                defaults={
                    'name': 'فتاحات أبواب الجراج',
                    'slug': 'garage-door-openers',
                    'is_active': True,
                }
            )
            
            # Process each product
            for product_data in unique_products:
                try:
                    title = product_data.get('title', '')
                    model_number = self.extract_model_number(title)
                    
                    # Check if exists
                    if model_number:
                        existing = Product.objects.filter(model_number=model_number).first()
                        if existing:
                            logger.info(f"Product {model_number} already exists, skipping...")
                            self.skipped_count += 1
                            continue
                    else:
                        existing = Product.objects.filter(name_en=title).first()
                        if existing:
                            logger.info(f"Product '{title}' already exists, skipping...")
                            self.skipped_count += 1
                            continue
                    
                    # Fetch additional details if requested
                    description = f"فتاحة أبواب جراج من LiftMaster - {title}"
                    features = "منتج أصلي من LiftMaster\nجودة عالية\nضمان من الشركة المصنعة"
                    
                    if fetch_details and product_data.get('url'):
                        try:
                            self.driver.get(product_data['url'])
                            time.sleep(2)
                            
                            # Try to find description
                            try:
                                desc_elem = self.driver.find_element(By.CSS_SELECTOR, '.description, .product-description, p')
                                if desc_elem:
                                    description = desc_elem.text.strip()
                            except:
                                pass
                            
                            # Try to find features
                            try:
                                features_list = self.driver.find_elements(By.CSS_SELECTOR, '.features li, ul li')
                                if features_list:
                                    features = '\n'.join([f.text.strip() for f in features_list[:10] if f.text.strip()])
                            except:
                                pass
                        except Exception as e:
                            logger.error(f"Error fetching details for {title}: {e}")
                    
                    # Create product
                    product = Product(
                        name=title,
                        name_en=title,
                        slug=slugify(title),
                        model_number=model_number or '',
                        category=category,
                        product_type='opener',
                        brand='LiftMaster',
                        short_description=f"LiftMaster {model_number or 'Garage Door Opener'}",
                        description=description,
                        features=features,
                        is_active=True,
                    )
                    
                    # Download and save image
                    if product_data.get('image_url'):
                        image_file = self.download_image(product_data['image_url'])
                        if image_file:
                            product.image = image_file
                    
                    product.save()
                    
                    logger.info(f"Successfully saved product: {title}")
                    self.scraped_count += 1
                    
                    # Be nice to the server
                    time.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error processing product: {e}")
                    self.error_count += 1
                    continue
            
            return {
                'success': True,
                'message': f'Successfully scraped {self.scraped_count} products',
                'scraped': self.scraped_count,
                'skipped': self.skipped_count,
                'errors': self.error_count
            }
            
        except Exception as e:
            logger.error(f"Error during scraping: {e}", exc_info=True)
            return {
                'success': False,
                'message': str(e),
                'scraped': self.scraped_count,
                'skipped': self.skipped_count,
                'errors': self.error_count
            }
        finally:
            self.close_driver()


def scrape_with_selenium(fetch_details=False):
    """
    Convenience function to scrape with Selenium
    """
    scraper = EnhancedLiftMasterScraper()
    return scraper.scrape_all_products(fetch_details=fetch_details)

