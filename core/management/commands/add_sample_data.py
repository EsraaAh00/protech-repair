# core/management/commands/add_sample_data.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from services.models import Service, ServiceCategory
from products.models import Product, ProductCategory
from inquiries.models import RecentWork


class Command(BaseCommand):
    help = 'Add sample data for testing the home page'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Adding sample data...'))

        # Create Service Categories
        service_cat, _ = ServiceCategory.objects.get_or_create(
            name='Repair Services',
            name_en='Repair Services',
            defaults={
                'description': 'Professional repair services',
                'icon': 'fa-wrench',
                'order': 1
            }
        )

        # Create Services
        services_data = [
            {
                'title': 'Emergency Repairs',
                'title_en': 'Emergency Repairs',
                'short_description': '24/7 emergency garage door repair services. We\'re here when you need us most.',
                'description': '24/7 emergency garage door repair services. Fast response time.',
                'icon': 'fa-tools',
                'category': service_cat,
                'is_active': True,
                'order': 1
            },
            {
                'title': 'Maintenance',
                'title_en': 'Maintenance',
                'short_description': 'Regular maintenance to keep your garage door running smoothly and safely.',
                'description': 'Professional maintenance services to extend the life of your garage door.',
                'icon': 'fa-cog',
                'category': service_cat,
                'is_active': True,
                'order': 2
            },
            {
                'title': 'Spring Replacement',
                'title_en': 'Spring Replacement',
                'short_description': 'Expert spring replacement services for all types of garage door systems.',
                'description': 'Professional spring replacement for all garage door models.',
                'icon': 'fa-wrench',
                'category': service_cat,
                'is_active': True,
                'order': 3
            }
        ]

        for service_data in services_data:
            Service.objects.get_or_create(
                slug=service_data['title_en'].lower().replace(' ', '-'),
                defaults=service_data
            )

        self.stdout.write(self.style.SUCCESS(f'Created {len(services_data)} services'))

        # Create Product Categories
        opener_cat, _ = ProductCategory.objects.get_or_create(
            name='Garage Door Openers',
            name_en='Garage Door Openers',
            defaults={
                'description': 'Smart garage door openers',
                'icon': 'fa-cog',
                'order': 1
            }
        )

        door_cat, _ = ProductCategory.objects.get_or_create(
            name='Garage Doors',
            name_en='Garage Doors',
            defaults={
                'description': 'Quality garage doors',
                'icon': 'fa-door-open',
                'order': 2
            }
        )

        # Create Openers (8 openers for slider)
        openers_data = [
            {
                'name': 'Smart WiFi Opener LM80',
                'name_en': 'Smart WiFi Opener LM80',
                'model_number': 'LM80',
                'short_description': 'WiFi enabled smart garage door opener with smartphone control',
                'description': 'Advanced smart garage door opener with WiFi connectivity and battery backup.',
                'features': 'Smart WiFi-enabled\nBelt drive system\nSmartphone control\nBattery backup\nProfessional installation',
                'category': opener_cat,
                'product_type': 'opener',
                'price': 299.00,
                'is_active': True,
                'order': 1
            },
            {
                'name': 'Belt Drive Opener LM100',
                'name_en': 'Belt Drive Opener LM100',
                'model_number': 'LM100',
                'short_description': 'Ultra-quiet belt drive garage door opener',
                'description': 'Quiet and powerful belt drive opener perfect for homes.',
                'features': 'Belt drive\nQuiet operation\nSmartphone app\nBattery backup',
                'category': opener_cat,
                'product_type': 'opener',
                'price': 349.00,
                'is_active': True,
                'order': 2
            },
            {
                'name': 'Chain Drive Opener CD500',
                'name_en': 'Chain Drive Opener CD500',
                'model_number': 'CD500',
                'short_description': 'Powerful chain drive for heavy doors',
                'description': 'Durable chain drive opener for heavy-duty applications.',
                'features': 'Chain drive\n1/2 HP motor\nDurable construction\nLong-lasting',
                'category': opener_cat,
                'product_type': 'opener',
                'price': 249.00,
                'is_active': True,
                'order': 3
            },
            {
                'name': 'Smart Opener Pro MAX',
                'name_en': 'Smart Opener Pro MAX',
                'model_number': 'PRO-MAX',
                'short_description': 'Premium smart opener with camera',
                'description': 'Top-of-the-line opener with integrated camera and smart features.',
                'features': 'WiFi\nIntegrated camera\nSmart alerts\nPremium quality',
                'category': opener_cat,
                'product_type': 'opener',
                'price': 499.00,
                'is_active': True,
                'order': 4
            },
            {
                'name': 'Wall Mount Opener WM1000',
                'name_en': 'Wall Mount Opener WM1000',
                'model_number': 'WM1000',
                'short_description': 'Space-saving wall mount opener',
                'description': 'Compact wall mount design saves ceiling space.',
                'features': 'Wall mount\nSpace-saving\nQuiet\nModern design',
                'category': opener_cat,
                'product_type': 'opener',
                'price': 399.00,
                'is_active': True,
                'order': 5
            },
            {
                'name': 'Battery Backup Opener BB200',
                'name_en': 'Battery Backup Opener BB200',
                'model_number': 'BB200',
                'short_description': 'Reliable opener with extended battery backup',
                'description': 'Never get locked out during power outages.',
                'features': 'Extended battery\nReliable\nQuiet belt drive\nSmart features',
                'category': opener_cat,
                'product_type': 'opener',
                'price': 329.00,
                'is_active': True,
                'order': 6
            },
            {
                'name': 'Jackshaft Opener JS300',
                'name_en': 'Jackshaft Opener JS300',
                'model_number': 'JS300',
                'short_description': 'Side-mount jackshaft opener',
                'description': 'Perfect for garages with limited ceiling space.',
                'features': 'Side-mount\nSpace-efficient\nPowerful motor\nQuiet',
                'category': opener_cat,
                'product_type': 'opener',
                'price': 449.00,
                'is_active': True,
                'order': 7
            },
            {
                'name': 'Economy Opener ECO100',
                'name_en': 'Economy Opener ECO100',
                'model_number': 'ECO100',
                'short_description': 'Affordable and reliable opener',
                'description': 'Budget-friendly without compromising quality.',
                'features': 'Affordable\nReliable\nEasy to use\nBasic features',
                'category': opener_cat,
                'product_type': 'opener',
                'price': 199.00,
                'is_active': True,
                'order': 8
            }
        ]

        for opener_data in openers_data:
            Product.objects.get_or_create(
                model_number=opener_data['model_number'],
                defaults=opener_data
            )

        self.stdout.write(self.style.SUCCESS(f'Created {len(openers_data)} openers'))

        # Create Doors (8 doors for slider)
        doors_data = [
            {
                'name': 'Traditional Steel Door',
                'name_en': 'Traditional Steel Door',
                'model_number': 'TSD-001',
                'short_description': 'Classic raised panel design',
                'description': 'Durable steel garage door with traditional raised panel design.',
                'category': door_cat,
                'product_type': 'door',
                'price': 899.00,
                'is_active': True,
                'order': 1
            },
            {
                'name': 'Modern Aluminum Door',
                'name_en': 'Modern Aluminum Door',
                'model_number': 'MAD-002',
                'short_description': 'Contemporary aluminum design',
                'description': 'Sleek modern aluminum garage door perfect for contemporary homes.',
                'category': door_cat,
                'product_type': 'door',
                'price': 1299.00,
                'is_active': True,
                'order': 2
            },
            {
                'name': 'Carriage House Door',
                'name_en': 'Carriage House Door',
                'model_number': 'CHD-003',
                'short_description': 'Elegant wood-like appearance',
                'description': 'Beautiful carriage house style door with authentic wood appearance.',
                'category': door_cat,
                'product_type': 'door',
                'price': 1499.00,
                'is_active': True,
                'order': 3
            },
            {
                'name': 'Custom Glass Door',
                'name_en': 'Custom Glass Door',
                'model_number': 'CGD-004',
                'short_description': 'Personalized glass designs',
                'description': 'Custom designed glass garage door for unique architectural styles.',
                'category': door_cat,
                'product_type': 'door',
                'price': 1799.00,
                'is_active': True,
                'order': 4
            },
            {
                'name': 'Insulated Steel Door',
                'name_en': 'Insulated Steel Door',
                'model_number': 'ISD-005',
                'short_description': 'Energy-efficient insulated door',
                'description': 'R-16 insulated steel door for energy efficiency.',
                'category': door_cat,
                'product_type': 'door',
                'price': 1099.00,
                'is_active': True,
                'order': 5
            },
            {
                'name': 'Wood-Look Composite Door',
                'name_en': 'Wood-Look Composite Door',
                'model_number': 'WLC-006',
                'short_description': 'Maintenance-free wood appearance',
                'description': 'Beautiful wood look without the maintenance.',
                'category': door_cat,
                'product_type': 'door',
                'price': 1399.00,
                'is_active': True,
                'order': 6
            },
            {
                'name': 'Contemporary Flush Door',
                'name_en': 'Contemporary Flush Door',
                'model_number': 'CFD-007',
                'short_description': 'Sleek flush panel design',
                'description': 'Modern flush design for contemporary architecture.',
                'category': door_cat,
                'product_type': 'door',
                'price': 1199.00,
                'is_active': True,
                'order': 7
            },
            {
                'name': 'Premium Custom Door',
                'name_en': 'Premium Custom Door',
                'model_number': 'PCD-008',
                'short_description': 'Fully customizable premium door',
                'description': 'Design your perfect garage door with our premium options.',
                'category': door_cat,
                'product_type': 'door',
                'price': 2499.00,
                'is_active': True,
                'order': 8
            }
        ]

        for door_data in doors_data:
            Product.objects.get_or_create(
                model_number=door_data['model_number'],
                defaults=door_data
            )

        self.stdout.write(self.style.SUCCESS(f'Created {len(doors_data)} doors'))

        # Create Recent Works
        works_data = [
            {
                'title': 'Modern Aluminum Door Installation',
                'description': 'Residential Installation - Los Angeles, CA. Complete installation of modern aluminum garage door.',
                'is_active': True,
                'order': 1
            },
            {
                'title': 'Emergency Spring Repair',
                'description': 'Same-Day Service - Beverly Hills, CA. Quick emergency spring replacement.',
                'is_active': True,
                'order': 2
            },
            {
                'title': 'Smart Opener Installation',
                'description': 'WiFi Enabled - Santa Monica, CA. Professional installation of smart WiFi opener.',
                'is_active': True,
                'order': 3
            }
        ]

        for work_data in works_data:
            RecentWork.objects.get_or_create(
                title=work_data['title'],
                defaults=work_data
            )

        self.stdout.write(self.style.SUCCESS(f'Created {len(works_data)} recent works'))
        self.stdout.write(self.style.SUCCESS('Sample data added successfully!'))

