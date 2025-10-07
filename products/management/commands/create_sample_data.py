from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from products.models import Product, Car, RealEstate, HotelBooking, ProductImage
from categories.models import Category
from django.utils import timezone
from datetime import timedelta
import random
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'إنشاء بيانات تجريبية للموقع'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=10,
            help='عدد المستخدمين المراد إنشاؤهم'
        )
        parser.add_argument(
            '--products',
            type=int,
            default=50,
            help='عدد المنتجات المراد إنشاؤها'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 بدء إنشاء البيانات التجريبية...'))
        
        # إنشاء الفئات
        self.create_categories()
        
        # إنشاء المستخدمين
        self.create_users(options['users'])
        
        # إنشاء المنتجات
        self.create_products(options['products'])
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ تم إنشاء البيانات التجريبية بنجاح!\n'
                f'المستخدمين: {options["users"]}\n'
                f'المنتجات: {options["products"]}'
            )
        )

    def create_categories(self):
        """إنشاء الفئات الأساسية"""
        categories_data = [
            {
                'name': 'السيارات',
                'slug': 'cars'
            },
            {
                'name': 'العقارات',
                'slug': 'real-estate'
            },
            {
                'name': 'الفنادق',
                'slug': 'hotels'
            },
            {
                'name': 'الإلكترونيات',
                'slug': 'electronics'
            },
            {
                'name': 'الملابس',
                'slug': 'clothing'
            },
            {
                'name': 'الكتب',
                'slug': 'books'
            }
        ]
        
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'slug': cat_data['slug']}
            )
            if created:
                self.stdout.write(f'✓ تم إنشاء فئة: {category.name}')

    def create_users(self, count):
        """إنشاء مستخدمين تجريبيين"""
        saudi_names = [
            'أحمد محمد', 'فاطمة علي', 'محمد عبدالله', 'نورا أحمد', 'سالم محمد',
            'عائشة عبدالرحمن', 'عبدالعزيز سعد', 'مريم خالد', 'يوسف عبدالله', 'زينب محمد'
        ]
        
        for i in range(count):
            name = random.choice(saudi_names)
            first_name, last_name = name.split()
            username = f'user_{i+1}'
            email = f'{username}@dalalsaudi.com'
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'is_active': True,
                    'date_joined': timezone.now() - timedelta(days=random.randint(1, 365))
                }
            )
            
            if created:
                user.set_password('123456')
                user.save()
                self.stdout.write(f'✓ تم إنشاء مستخدم: {user.username}')

    def create_products(self, count):
        """إنشاء منتجات تجريبية"""
        categories = Category.objects.all()
        users = User.objects.all()
        
        if not categories.exists() or not users.exists():
            self.stdout.write(
                self.style.ERROR('خطأ: يجب إنشاء الفئات والمستخدمين أولاً')
            )
            return
        
        # بيانات تجريبية للمنتجات
        car_data = [
            ('تويوتا كامري 2022', 'سيارة عائلية فاخرة', 85000, 'Toyota', 'Camry', 2022, 15000),
            ('فورد موستانج 2021', 'سيارة رياضية قوية', 125000, 'Ford', 'Mustang', 2021, 25000),
            ('نيسان التيما 2020', 'سيارة اقتصادية', 65000, 'Nissan', 'Altima', 2020, 45000),
            ('مرسيدس بنز C300', 'سيارة فاخرة', 185000, 'Mercedes', 'C300', 2023, 8000),
            ('بي إم دبليو X5', 'سيارة دفع رباعي', 225000, 'BMW', 'X5', 2022, 12000),
        ]
        
        real_estate_data = [
            ('شقة فاخرة في الرياض', 'شقة 3 غرف وصالة', 450000, 'apartment', 120, 3, 2, False),
            ('فيلا في جدة', 'فيلا دورين مع حديقة', 1200000, 'villa', 300, 5, 4, True),
            ('أرض في الدمام', 'أرض سكنية في موقع مميز', 350000, 'land', 500, None, None, False),
            ('محل تجاري', 'محل في مركز تجاري', 180000, 'commercial', 80, None, None, False),
            ('شقة للإيجار', 'شقة مفروشة غرفتين', 2500, 'apartment', 90, 2, 1, True),
        ]
        
        hotel_data = [
            ('فندق الرياض الفاخر', 'غرفة مزدوجة لليلة واحدة', 450, 'فندق الرياض', 'double', 2),
            ('منتجع جدة', 'جناح عائلي لثلاث ليالي', 850, 'منتجع جدة', 'family', 4),
            ('فندق الدمام', 'غرفة فردية', 280, 'فندق الدمام', 'single', 1),
            ('فندق مكة', 'جناح فاخر', 650, 'فندق مكة', 'suite', 2),
            ('منتجع المدينة', 'غرفة مزدوجة', 380, 'منتجع المدينة', 'double', 2),
        ]
        
        created_count = 0
        
        for i in range(count):
            category = random.choice(categories)
            user = random.choice(users)
            
            # إنشاء المنتج الأساسي
            if category.name == 'السيارات' and car_data:
                data = random.choice(car_data)
                title, description, price, make, model, year, mileage = data
                title = f"{title} - {i+1}"
            elif category.name == 'العقارات' and real_estate_data:
                data = random.choice(real_estate_data)
                title, description, price, prop_type, area, beds, baths, furnished = data
                title = f"{title} - {i+1}"
            elif category.name == 'الفنادق' and hotel_data:
                data = random.choice(hotel_data)
                title, description, price, hotel_name, room_type, guests = data
                title = f"{title} - {i+1}"
            else:
                title = f'منتج تجريبي {i+1}'
                description = f'وصف المنتج التجريبي رقم {i+1}'
                price = random.randint(100, 10000)
            
            # إنشاء المنتج
            product = Product.objects.create(
                title=title,
                description=description,
                price=Decimal(str(price)),
                category=category,
                seller=user,
                location_latitude=Decimal('24.7136'),  # الرياض
                location_longitude=Decimal('46.6753'),
                status=random.choice(['pending_approval', 'active', 'sold', 'hidden']),
                is_approved=random.choice([True, False]),
                views_count=random.randint(0, 500),
                created_at=timezone.now() - timedelta(days=random.randint(1, 30))
            )
            
            # إضافة تفاصيل خاصة بالفئة
            if category.name == 'السيارات' and car_data:
                Car.objects.create(
                    product=product,
                    make=make,
                    model=model,
                    year=year,
                    mileage=mileage,
                    transmission_type=random.choice(['automatic', 'manual']),
                    fuel_type=random.choice(['gasoline', 'diesel', 'hybrid']),
                    color=random.choice(['أبيض', 'أسود', 'رمادي', 'أزرق', 'أحمر']),
                    is_new=random.choice([True, False])
                )
            
            elif category.name == 'العقارات' and real_estate_data:
                RealEstate.objects.create(
                    product=product,
                    property_type=prop_type,
                    area_sqm=Decimal(str(area)),
                    num_bedrooms=beds,
                    num_bathrooms=baths,
                    is_furnished=furnished,
                    for_rent=price < 10000  # إذا كان السعر قليل فهو للإيجار
                )
            
            elif category.name == 'الفنادق' and hotel_data:
                check_in = timezone.now().date() + timedelta(days=random.randint(1, 30))
                check_out = check_in + timedelta(days=random.randint(1, 7))
                
                HotelBooking.objects.create(
                    product=product,
                    hotel_name=hotel_name,
                    room_type=room_type,
                    num_guests=guests,
                    check_in_date=check_in,
                    check_out_date=check_out
                )
            
            created_count += 1
            if created_count % 10 == 0:
                self.stdout.write(f'✓ تم إنشاء {created_count} منتج...')
        
        self.stdout.write(f'✅ تم إنشاء {created_count} منتج بنجاح!') 