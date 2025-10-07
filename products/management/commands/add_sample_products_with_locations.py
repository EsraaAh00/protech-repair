from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from products.models import Product, ProductImage, Car, RealEstate, HotelBooking
from categories.models import Category
from decimal import Decimal
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'إضافة منتجات تجريبية مع إحداثيات جغرافية'

    def handle(self, *args, **options):
        # إنشاء مستخدم تجريبي إذا لم يكن موجوداً
        user, created = User.objects.get_or_create(
            username='demo_seller',
            defaults={
                'email': 'demo@example.com',
                'first_name': 'أحمد',
                'last_name': 'محمد',
                'is_seller': True
            }
        )
        
        if created:
            user.set_password('demo123')
            user.save()
            self.stdout.write(self.style.SUCCESS('تم إنشاء المستخدم التجريبي'))

        # إحداثيات مدن سعودية
        cities = [
            {'name': 'الرياض', 'lat': 24.7136, 'lng': 46.6753},
            {'name': 'جدة', 'lat': 21.4858, 'lng': 39.1925},
            {'name': 'الدمام', 'lat': 26.4207, 'lng': 50.0888},
            {'name': 'مكة المكرمة', 'lat': 21.3891, 'lng': 39.8579},
            {'name': 'المدينة المنورة', 'lat': 24.5247, 'lng': 39.5692},
            {'name': 'الطائف', 'lat': 21.2703, 'lng': 40.4034},
            {'name': 'تبوك', 'lat': 28.3998, 'lng': 36.5700},
            {'name': 'بريدة', 'lat': 26.3260, 'lng': 43.9750},
        ]

        # بيانات السيارات
        cars_data = [
            {
                'title': 'تويوتا كامري 2022 - حالة ممتازة',
                'description': 'سيارة تويوتا كامري موديل 2022 بحالة ممتازة، مكيف بارد، جير أوتوماتيك، فحص كامل',
                'price': Decimal('85000.00'),
                'make': 'Toyota',
                'model': 'Camry',
                'year': 2022,
                'mileage': 25000,
                'transmission_type': 'automatic',
                'fuel_type': 'gasoline',
                'color': 'أبيض',
                'is_new': False
            },
            {
                'title': 'هوندا أكورد 2021 للبيع',
                'description': 'هوندا أكورد 2021، صيانة دورية منتظمة، بصمة تشغيل، شاشة تاتش',
                'price': Decimal('78000.00'),
                'make': 'Honda',
                'model': 'Accord',
                'year': 2021,
                'mileage': 35000,
                'transmission_type': 'automatic',
                'fuel_type': 'gasoline',
                'color': 'أسود',
                'is_new': False
            },
            {
                'title': 'هيونداي إلنترا 2023 جديدة',
                'description': 'هيونداي إلنترا 2023 جديدة بالكامل، ضمان الوكالة، مواصفات خليجية',
                'price': Decimal('65000.00'),
                'make': 'Hyundai',
                'model': 'Elantra',
                'year': 2023,
                'mileage': 5000,
                'transmission_type': 'automatic',
                'fuel_type': 'gasoline',
                'color': 'فضي',
                'is_new': True
            },
            {
                'title': 'نيسان التيما 2020',
                'description': 'نيسان التيما 2020، جير أوتوماتيك، مكيف ثلج، تأمين شامل',
                'price': Decimal('55000.00'),
                'make': 'Nissan',
                'model': 'Altima',
                'year': 2020,
                'mileage': 45000,
                'transmission_type': 'automatic',
                'fuel_type': 'gasoline',
                'color': 'أحمر',
                'is_new': False
            },
            {
                'title': 'كيا سيراتو 2022',
                'description': 'كيا سيراتو 2022، اقتصادية في استهلاك الوقود، مناسبة للعائلات',
                'price': Decimal('48000.00'),
                'make': 'Kia',
                'model': 'Cerato',
                'year': 2022,
                'mileage': 18000,
                'transmission_type': 'automatic',
                'fuel_type': 'gasoline',
                'color': 'أزرق',
                'is_new': False
            },
            {
                'title': 'BMW 320i 2021 فل كامل',
                'description': 'BMW 320i 2021 فل كامل، جلد، فتحة سقف، نظام ملاحة، حالة ممتازة',
                'price': Decimal('145000.00'),
                'make': 'BMW',
                'model': '320i',
                'year': 2021,
                'mileage': 28000,
                'transmission_type': 'automatic',
                'fuel_type': 'gasoline',
                'color': 'أسود',
                'is_new': False
            },
            {
                'title': 'مرسيدس C200 2022',
                'description': 'مرسيدس C200 2022، مواصفات أوروبية، حالة الوكالة',
                'price': Decimal('165000.00'),
                'make': 'Mercedes',
                'model': 'C200',
                'year': 2022,
                'mileage': 15000,
                'transmission_type': 'automatic',
                'fuel_type': 'gasoline',
                'color': 'أبيض لؤلؤي',
                'is_new': False
            },
            {
                'title': 'لكزس ES350 2023',
                'description': 'لكزس ES350 2023، هايبرد، توفير في الوقود، تقنيات متقدمة',
                'price': Decimal('185000.00'),
                'make': 'Lexus',
                'model': 'ES350',
                'year': 2023,
                'mileage': 8000,
                'transmission_type': 'automatic',
                'fuel_type': 'hybrid',
                'color': 'فضي',
                'is_new': False
            }
        ]

        # البحث عن فئة السيارات أو إنشاؤها
        cars_category, created = Category.objects.get_or_create(
            name='السيارات',
            defaults={
                'slug': 'cars',
                'description': 'فئة السيارات المستعملة والجديدة'
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS('تم إنشاء فئة السيارات'))

        products_created = 0
        
        for i, car_data in enumerate(cars_data):
            city = cities[i % len(cities)]
            
            # إضافة تشويش صغير للإحداثيات
            lat_offset = random.uniform(-0.05, 0.05)
            lng_offset = random.uniform(-0.05, 0.05)
            
            # إنشاء المنتج
            product = Product.objects.create(
                title=car_data['title'],
                description=car_data['description'],
                price=car_data['price'],
                category=cars_category,
                seller=user,
                location_latitude=Decimal(str(city['lat'] + lat_offset)),
                location_longitude=Decimal(str(city['lng'] + lng_offset)),
                status='active',
                is_approved=True,
                views_count=random.randint(10, 500)
            )
            
            # إنشاء تفاصيل السيارة
            Car.objects.create(
                product=product,
                make=car_data['make'],
                model=car_data['model'],
                year=car_data['year'],
                mileage=car_data['mileage'],
                transmission_type=car_data['transmission_type'],
                fuel_type=car_data['fuel_type'],
                color=car_data['color'],
                is_new=car_data['is_new']
            )
            
            products_created += 1
            self.stdout.write(
                self.style.SUCCESS(f'تم إنشاء السيارة: {car_data["title"]} في {city["name"]}')
            )

        # إضافة بعض العقارات والفنادق أيضاً
        real_estate_category, created = Category.objects.get_or_create(
            name='العقارات',
            defaults={
                'slug': 'real-estate',
                'description': 'فئة العقارات للبيع والإيجار'
            }
        )

        hotels_category, created = Category.objects.get_or_create(
            name='الفنادق',
            defaults={
                'slug': 'hotels',
                'description': 'فئة حجوزات الفنادق'
            }
        )

        # إضافة عقار واحد
        city = random.choice(cities)
        real_estate_product = Product.objects.create(
            title='شقة للبيع في ' + city['name'],
            description='شقة 3 غرف وصالة، مطبخ مجهز، موقع مميز',
            price=Decimal('450000.00'),
            category=real_estate_category,
            seller=user,
            location_latitude=Decimal(str(city['lat'] + random.uniform(-0.02, 0.02))),
            location_longitude=Decimal(str(city['lng'] + random.uniform(-0.02, 0.02))),
            status='active',
            is_approved=True,
            views_count=random.randint(20, 200)
        )

        RealEstate.objects.create(
            product=real_estate_product,
            property_type='apartment',
            area_sqm=Decimal('120.50'),
            num_bedrooms=3,
            num_bathrooms=2,
            is_furnished=True,
            for_rent=False
        )

        # إضافة فندق واحد
        city = random.choice(cities)
        hotel_product = Product.objects.create(
            title='حجز فندق 5 نجوم في ' + city['name'],
            description='غرفة مزدوجة فاخرة، إفطار مجاني، مسبح',
            price=Decimal('350.00'),
            category=hotels_category,
            seller=user,
            location_latitude=Decimal(str(city['lat'] + random.uniform(-0.01, 0.01))),
            location_longitude=Decimal(str(city['lng'] + random.uniform(-0.01, 0.01))),
            status='active',
            is_approved=True,
            views_count=random.randint(50, 300)
        )

        from datetime import date, timedelta
        HotelBooking.objects.create(
            product=hotel_product,
            hotel_name='فندق الرياض الفاخر',
            room_type='double',
            num_guests=2,
            check_in_date=date.today() + timedelta(days=30),
            check_out_date=date.today() + timedelta(days=33)
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'تم إنشاء {products_created} سيارة + عقار واحد + فندق واحد بنجاح مع إحداثيات جغرافية!'
            )
        ) 