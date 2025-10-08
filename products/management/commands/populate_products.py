# products/management/commands/populate_products.py
from django.core.management.base import BaseCommand
from products.models import ProductCategory, Product, OpenerSpecifications, DoorSpecifications
from decimal import Decimal


class Command(BaseCommand):
    help = 'Populate initial products and product categories'
    
    def handle(self, *args, **options):
        self.stdout.write('Creating product categories...')
        
        # Create Product Categories
        openers_category, _ = ProductCategory.objects.get_or_create(
            name='فتاحات أبواب الجراج',
            name_en='Garage Door Openers',
            defaults={
                'slug': 'garage-door-openers',
                'description': 'فتاحات أبواب الجراج الحديثة مع ميزات ذكية',
                'icon': 'fa-power-off',
                'order': 1
            }
        )
        
        doors_category, _ = ProductCategory.objects.get_or_create(
            name='أبواب الجراج',
            name_en='Garage Doors',
            defaults={
                'slug': 'garage-doors',
                'description': 'أبواب جراج بتصاميم وأنماط متنوعة',
                'icon': 'fa-door-closed',
                'order': 2
            }
        )
        
        accessories_category, _ = ProductCategory.objects.get_or_create(
            name='الإكسسوارات وقطع الغيار',
            name_en='Accessories & Parts',
            defaults={
                'slug': 'accessories-parts',
                'description': 'إكسسوارات وقطع غيار أبواب الجراج',
                'icon': 'fa-puzzle-piece',
                'order': 3
            }
        )
        
        self.stdout.write(self.style.SUCCESS('Product categories created!'))
        
        # Create Opener Products
        openers_data = [
            {
                'name': 'فتاحة سلسلة 1/2 حصان',
                'name_en': 'Chain Drive 1/2 HP Opener',
                'model_number': '8500W',
                'category': openers_category,
                'product_type': 'opener',
                'brand': 'LiftMaster',
                'short_description': 'فتاحة أبواب جراج بمحرك سلسلة قوية',
                'description': 'فتاحة LiftMaster 8500W بنظام محرك سلسلة قوي ومتين. مثالية للأبواب السكنية القياسية.',
                'features': '''محرك سلسلة قوي
قوة 1/2 حصان
نظام أمان متقدم
تشغيل هادئ نسبياً
ضمان 5 سنوات على المحرك''',
                'specifications': '''القوة: 1/2 HP
النوع: Chain Drive
الضمان: 5 years motor
الإضاءة: 100W LED''',
                'price': Decimal('299.99'),
                'is_featured': True,
                'is_best_seller': True,
                'order': 1,
                'opener_specs': {
                    'drive_type': 'chain',
                    'horsepower': '1/2 HP',
                    'has_wifi': False,
                    'has_battery_backup': False,
                    'has_camera': False,
                    'has_smart_features': False,
                    'lifting_capacity': 'Up to 400 lbs',
                    'speed': '7 inches/second',
                    'noise_level': 'Moderate',
                    'warranty_years': 5
                }
            },
            {
                'name': 'فتاحة حزام ذكية مع Wi-Fi',
                'name_en': 'Belt Drive Smart Opener with Wi-Fi',
                'model_number': '8160WB',
                'category': openers_category,
                'product_type': 'opener',
                'brand': 'LiftMaster',
                'short_description': 'فتاحة هادئة مع ميزات ذكية وبطارية احتياطية',
                'description': 'فتاحة LiftMaster 8160WB بنظام حزام فائق الهدوء مع Wi-Fi مدمج وبطارية احتياطية.',
                'features': '''تشغيل فائق الهدوء
Wi-Fi مدمج (myQ)
بطارية احتياطية
تطبيق ذكي للتحكم عن بعد
إضاءة LED ساطعة
ضمان مدى الحياة على المحرك''',
                'specifications': '''القوة: 3/4 HP
النوع: Belt Drive
Wi-Fi: Built-in myQ
البطارية الاحتياطية: نعم
الضمان: Lifetime motor''',
                'price': Decimal('449.99'),
                'is_featured': True,
                'is_best_seller': True,
                'order': 2,
                'opener_specs': {
                    'drive_type': 'belt',
                    'horsepower': '3/4 HP',
                    'has_wifi': True,
                    'has_battery_backup': True,
                    'has_camera': False,
                    'has_smart_features': True,
                    'lifting_capacity': 'Up to 500 lbs',
                    'speed': '8 inches/second',
                    'noise_level': 'Ultra Quiet',
                    'warranty_years': 99  # Lifetime
                }
            },
            {
                'name': 'فتاحة جدارية مع كاميرا',
                'name_en': 'Wall Mount Opener with Camera',
                'model_number': '87504-267',
                'category': openers_category,
                'product_type': 'opener',
                'brand': 'LiftMaster',
                'short_description': 'فتاحة جدارية مع كاميرا وإضاءة LED متطورة',
                'description': 'فتاحة LiftMaster 87504-267 توفر أقصى مساحة في السقف مع كاميرا مدمجة وإضاءة LED من الزاوية للزاوية.',
                'features': '''تصميم جداري لتوفير المساحة
كاميرا HD مدمجة
إضاءة LED من الزاوية للزاوية
Wi-Fi مدمج
بطارية احتياطية
تشغيل فائق الهدوء
ضمان مدى الحياة''',
                'specifications': '''النوع: Wall Mount (Jackshaft)
الكاميرا: HD Camera
Wi-Fi: myQ Built-in
البطارية: Battery Backup
الإضاءة: Corner to Corner LED''',
                'price': Decimal('699.99'),
                'is_featured': True,
                'is_new': True,
                'order': 3,
                'opener_specs': {
                    'drive_type': 'wall_mount',
                    'horsepower': '3/4 HP',
                    'has_wifi': True,
                    'has_battery_backup': True,
                    'has_camera': True,
                    'has_smart_features': True,
                    'lifting_capacity': 'Up to 600 lbs',
                    'speed': '9 inches/second',
                    'noise_level': 'Ultra Quiet',
                    'warranty_years': 99
                }
            },
        ]
        
        self.stdout.write('Creating opener products...')
        for opener_data in openers_data:
            opener_specs = opener_data.pop('opener_specs')
            product, created = Product.objects.get_or_create(
                model_number=opener_data['model_number'],
                defaults=opener_data
            )
            
            if created:
                # Create opener specifications
                OpenerSpecifications.objects.create(
                    product=product,
                    **opener_specs
                )
                self.stdout.write(f'  Created: {product.name}')
            else:
                self.stdout.write(f'  Already exists: {product.name}')
        
        # Create Door Products
        doors_data = [
            {
                'name': 'باب جراج بلوحات طويلة',
                'name_en': 'Long Panel Garage Door',
                'model_number': 'LP-100',
                'category': doors_category,
                'product_type': 'door',
                'brand': 'Clopay',
                'short_description': 'باب جراج تقليدي بلوحات طويلة',
                'description': 'باب جراج Clopay بتصميم اللوحات الطويلة الكلاسيكي. متوفر بألوان وأحجام متعددة.',
                'features': '''تصميم كلاسيكي
مادة فولاذية متينة
عزل حراري
ألوان متعددة
سهل الصيانة''',
                'specifications': '''المادة: Steel
العزل: R-12
الضمان: 10 years''',
                'price': Decimal('899.99'),
                'is_featured': True,
                'order': 1,
                'door_specs': {
                    'panel_style': 'long_panel',
                    'material': 'steel',
                    'width_options': '8ft, 9ft, 16ft',
                    'height_options': '7ft, 8ft',
                    'insulation_type': 'double',
                    'r_value': 'R-12',
                    'color_options': '''White
Almond
Sandstone
Brown''',
                    'texture_options': 'Smooth, Woodgrain',
                    'has_windows': True,
                    'window_options': 'Various window styles available',
                    'warranty_years': 10
                }
            },
            {
                'name': 'باب جراج معاصر',
                'name_en': 'Contemporary Garage Door',
                'model_number': 'MOD-200',
                'category': doors_category,
                'product_type': 'door',
                'brand': 'Clopay',
                'short_description': 'باب جراج بتصميم عصري حديث',
                'description': 'باب جراج بتصميم معاصر مع خطوط نظيفة وأنيقة. خيارات زجاج كاملة أو جزئية.',
                'features': '''تصميم عصري أنيق
ألومنيوم أو فولاذ
خيارات زجاج متعددة
عزل ممتاز
مقاوم للطقس''',
                'specifications': '''المادة: Aluminum/Steel
العزل: R-16
الزجاج: متوفر
الضمان: 15 years''',
                'price': Decimal('1499.99'),
                'is_featured': True,
                'is_new': True,
                'order': 2,
                'door_specs': {
                    'panel_style': 'contemporary',
                    'material': 'aluminum',
                    'width_options': '8ft, 9ft, 10ft, 16ft',
                    'height_options': '7ft, 8ft, 9ft',
                    'insulation_type': 'double',
                    'r_value': 'R-16',
                    'color_options': '''Black
White
Bronze
Custom Colors Available''',
                    'texture_options': 'Smooth',
                    'has_windows': True,
                    'window_options': 'Full glass, partial glass, frosted',
                    'warranty_years': 15
                }
            },
        ]
        
        self.stdout.write('Creating door products...')
        for door_data in doors_data:
            door_specs = door_data.pop('door_specs')
            product, created = Product.objects.get_or_create(
                model_number=door_data['model_number'],
                defaults=door_data
            )
            
            if created:
                # Create door specifications
                DoorSpecifications.objects.create(
                    product=product,
                    **door_specs
                )
                self.stdout.write(f'  Created: {product.name}')
            else:
                self.stdout.write(f'  Already exists: {product.name}')
        
        self.stdout.write(self.style.SUCCESS('\nAll products created successfully!'))
        self.stdout.write(f'Total categories: {ProductCategory.objects.count()}')
        self.stdout.write(f'Total products: {Product.objects.count()}')

