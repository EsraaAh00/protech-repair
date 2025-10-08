"""
Management command to manually import LiftMaster products
Use this when automatic scraping doesn't work
"""
from django.core.management.base import BaseCommand
from products.models import Product, ProductCategory
from django.utils.text import slugify
from django.core.files.base import ContentFile
import requests


class Command(BaseCommand):
    help = 'Manually import LiftMaster products'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Importing LiftMaster Products Manually...'))
        
        # Get or create category
        category, _ = ProductCategory.objects.get_or_create(
            name_en='Garage Door Openers',
            defaults={
                'name': 'فتاحات أبواب الجراج',
                'slug': 'garage-door-openers',
                'is_active': True,
            }
        )
        
        # List of products from LiftMaster website
        # Based on the website content provided
        products_data = [
            {
                'name': 'LM-W8ME Sectional Garage Door Opener',
                'model_number': 'LM-W8ME',
                'description': 'فتاحة أبواب جراج قطاعية من LiftMaster - موديل LM-W8ME',
                'category': 'Sectional Garage Door',
            },
            {
                'name': 'LM3800TXSA Sectional Garage Door Opener',
                'model_number': 'LM3800TXSA',
                'description': 'فتاحة أبواب جراج قطاعية من LiftMaster - موديل LM3800TXSA',
                'category': 'Sectional Garage Door',
            },
            {
                'name': 'LM80EV DC Sectional Garage Door Opener',
                'model_number': 'LM80EV',
                'description': 'فتاحة أبواب جراج قطاعية DC من LiftMaster - موديل LM80EV',
                'category': 'Sectional Garage Door',
            },
            {
                'name': 'LM100EV Sectional Garage Door Opener',
                'model_number': 'LM100EV',
                'description': 'فتاحة أبواب جراج قطاعية من LiftMaster - موديل LM100EV',
                'category': 'Sectional Garage Door',
            },
            {
                'name': 'LM130EV Sectional Garage Door Opener',
                'model_number': 'LM130EV',
                'description': 'فتاحة أبواب جراج قطاعية من LiftMaster - موديل LM130EV',
                'category': 'Sectional Garage Door',
            },
            {
                'name': 'LM555EVGBSA Roller Garage Opener Weather Resistant',
                'model_number': 'LM555EVGBSA',
                'description': 'فتاحة أبواب رولر مقاومة للطقس من LiftMaster - موديل LM555EVGBSA',
                'category': 'Roller Garage Door',
            },
        ]
        
        imported = 0
        skipped = 0
        
        for product_data in products_data:
            try:
                # Check if exists
                existing = Product.objects.filter(
                    model_number=product_data['model_number']
                ).first()
                
                if existing:
                    self.stdout.write(f"⏭️  Skipped: {product_data['name']} (already exists)")
                    skipped += 1
                    continue
                
                # Create product
                product = Product.objects.create(
                    name=product_data['name'],
                    name_en=product_data['name'],
                    slug=slugify(product_data['name']),
                    model_number=product_data['model_number'],
                    category=category,
                    product_type='opener',
                    brand='LiftMaster',
                    description=product_data['description'],
                    short_description=f"{product_data['category']} - {product_data['model_number']}",
                    is_active=True,
                )
                
                self.stdout.write(self.style.SUCCESS(f"✅ Imported: {product_data['name']}"))
                imported += 1
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ Error importing {product_data['name']}: {e}"))
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'✅ Successfully imported {imported} products'))
        self.stdout.write(f'⏭️  Skipped {skipped} existing products')
        self.stdout.write('')
        self.stdout.write('Note: You can now add images and prices manually through the admin panel')


