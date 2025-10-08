"""
Management command to test and debug the scraper
"""
from django.core.management.base import BaseCommand
from products.scraper import LiftMasterScraper
import logging

logging.basicConfig(level=logging.INFO)


class Command(BaseCommand):
    help = 'Test the LiftMaster scraper and show debug information'

    def add_arguments(self, parser):
        parser.add_argument(
            '--save-html',
            action='store_true',
            help='Save HTML content to file for inspection',
        )
        parser.add_argument(
            '--url',
            type=str,
            default=None,
            help='Specific URL to test (default: products page)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Testing LiftMaster Scraper...'))
        self.stdout.write('')
        
        scraper = LiftMasterScraper()
        
        # Test URL
        test_url = options.get('url') or scraper.PRODUCTS_URL
        self.stdout.write(f'Testing URL: {test_url}')
        self.stdout.write('-' * 80)
        
        try:
            # Fetch the page
            response = scraper.session.get(test_url, timeout=30)
            
            self.stdout.write(f'Status Code: {response.status_code}')
            self.stdout.write(f'Content Length: {len(response.content)} bytes')
            self.stdout.write('')
            
            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f'Failed to fetch page: {response.status_code}'))
                return
            
            # Save HTML if requested
            if options['save_html']:
                filename = 'debug_page.html'
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                self.stdout.write(self.style.SUCCESS(f'HTML saved to: {filename}'))
                self.stdout.write('')
            
            # Try to find products
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.content, 'lxml')
            
            self.stdout.write(f"Page Title: {soup.title.string if soup.title else 'No title'}")
            self.stdout.write('')
            
            # Test different selectors
            self.stdout.write('Testing different selectors:')
            self.stdout.write('-' * 80)
            
            selectors = [
                ('Links with "product" in href', lambda: soup.find_all('a', href=lambda h: h and 'product' in h.lower())),
                ('H2 tags', lambda: soup.find_all('h2')),
                ('H3 tags', lambda: soup.find_all('h3')),
                ('All images', lambda: soup.find_all('img')),
                ('Divs with "product" class', lambda: soup.find_all('div', class_=lambda c: c and 'product' in c.lower() if c else False)),
                ('Articles', lambda: soup.find_all('article')),
                ('All links', lambda: soup.find_all('a', href=True)),
            ]
            
            for name, finder in selectors:
                try:
                    elements = finder()
                    self.stdout.write(f'{name}: {len(elements)} found')
                    
                    # Show first few
                    if elements and len(elements) > 0:
                        for i, elem in enumerate(elements[:3]):
                            if elem.name == 'a':
                                self.stdout.write(f'  - {elem.get("href", "")[:80]} | {elem.get_text(strip=True)[:50]}')
                            elif elem.name == 'img':
                                self.stdout.write(f'  - {elem.get("src", "")[:80]} | {elem.get("alt", "")[:50]}')
                            else:
                                self.stdout.write(f'  - {elem.get_text(strip=True)[:80]}')
                        self.stdout.write('')
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'{name}: Error - {e}'))
            
            self.stdout.write('')
            self.stdout.write('-' * 80)
            
            # Now try the actual scraper
            self.stdout.write('Running actual scraper...')
            self.stdout.write('')
            
            products = scraper.scrape_products_list()
            
            if products:
                self.stdout.write(self.style.SUCCESS(f'Found {len(products)} products!'))
                self.stdout.write('')
                
                for i, product in enumerate(products[:5], 1):
                    self.stdout.write(f"{i}. {product.get('title', 'No title')}")
                    self.stdout.write(f"   URL: {product.get('url', 'No URL')}")
                    self.stdout.write(f"   Image: {product.get('image_url', 'No image')[:80]}")
                    self.stdout.write('')
            else:
                self.stdout.write(self.style.WARNING('No products found'))
                self.stdout.write('')
                self.stdout.write('Suggestions:')
                self.stdout.write('1. Check the HTML file (use --save-html) to see the page structure')
                self.stdout.write('2. The website might use JavaScript to load products')
                self.stdout.write('3. The website structure might be different than expected')
                self.stdout.write('4. Try adding products manually using the manual_import command')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
            import traceback
            self.stdout.write(traceback.format_exc())


