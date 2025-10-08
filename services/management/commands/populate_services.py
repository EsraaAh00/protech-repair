# services/management/commands/populate_services.py
from django.core.management.base import BaseCommand
from services.models import ServiceCategory, Service


class Command(BaseCommand):
    help = 'Populate initial services and service categories'
    
    def handle(self, *args, **options):
        self.stdout.write('Creating service categories...')
        
        # Create Service Categories
        repair_category, _ = ServiceCategory.objects.get_or_create(
            name='خدمات الإصلاح',
            name_en='Repair Services',
            defaults={
                'slug': 'repair-services',
                'description': 'جميع خدمات الإصلاح والصيانة لأبواب الجراج',
                'icon': 'fa-wrench',
                'order': 1
            }
        )
        
        installation_category, _ = ServiceCategory.objects.get_or_create(
            name='خدمات التركيب',
            name_en='Installation Services',
            defaults={
                'slug': 'installation-services',
                'description': 'خدمات تركيب أبواب الجراج والفتاحات',
                'icon': 'fa-tools',
                'order': 2
            }
        )
        
        maintenance_category, _ = ServiceCategory.objects.get_or_create(
            name='خدمات الصيانة',
            name_en='Maintenance Services',
            defaults={
                'slug': 'maintenance-services',
                'description': 'خدمات الصيانة الدورية والفحص',
                'icon': 'fa-cog',
                'order': 3
            }
        )
        
        self.stdout.write(self.style.SUCCESS('Service categories created!'))
        
        # Create Services
        services_data = [
            {
                'title': 'إصلاح زنبرك الباب',
                'title_en': 'Spring Repair',
                'category': repair_category,
                'short_description': 'إصلاح واستبدال زنبركات أبواب الجراج المكسورة',
                'description': 'نقوم بإصلاح واستبدال جميع أنواع زنبركات أبواب الجراج (Torsion Springs و Extension Springs). خدمة سريعة ومضمونة.',
                'features': '''إصلاح فوري
ضمان سنة واحدة
قطع غيار أصلية
خدمة طوارئ متاحة''',
                'icon': 'fa-spring',
                'is_featured': True,
                'order': 1
            },
            {
                'title': 'إصلاح فتاحة الباب',
                'title_en': 'Opener Repair',
                'category': repair_category,
                'short_description': 'إصلاح وصيانة فتاحات أبواب الجراج',
                'description': 'إصلاح جميع أنواع فتاحات أبواب الجراج بما في ذلك Chain Drive، Belt Drive، Wall Mount. تشخيص دقيق وإصلاح سريع.',
                'features': '''تشخيص مجاني
إصلاح جميع الماركات
قطع غيار متوفرة
ضمان على الخدمة''',
                'icon': 'fa-power-off',
                'is_featured': True,
                'order': 2
            },
            {
                'title': 'إصلاح الكابلات والبكرات',
                'title_en': 'Cable & Roller Repair',
                'category': repair_category,
                'short_description': 'استبدال الكابلات والبكرات المتآكلة',
                'description': 'نوفر خدمة استبدال الكابلات والبكرات المتآكلة أو المكسورة. نستخدم قطع غيار عالية الجودة لضمان التشغيل السلس.',
                'features': '''فحص شامل
استبدال فوري
قطع غيار عالية الجودة
أسعار تنافسية''',
                'icon': 'fa-chain',
                'order': 3
            },
            {
                'title': 'تركيب باب جراج جديد',
                'title_en': 'New Door Installation',
                'category': installation_category,
                'short_description': 'تركيب احترافي لأبواب الجراج الجديدة',
                'description': 'نقوم بتركيب جميع أنواع أبواب الجراج بشكل احترافي. نوفر مجموعة واسعة من الأنماط والألوان.',
                'features': '''استشارة مجانية
تركيب احترافي
ضمان على التركيب
خيارات متعددة للتصميم''',
                'icon': 'fa-door-open',
                'is_featured': True,
                'order': 4
            },
            {
                'title': 'تركيب فتاحة الباب',
                'title_en': 'Opener Installation',
                'category': installation_category,
                'short_description': 'تركيب فتاحات أبواب الجراج الحديثة',
                'description': 'تركيب فتاحات أبواب الجراج مع ميزات ذكية مثل Wi-Fi والبطارية الاحتياطية والكاميرا.',
                'features': '''تركيب احترافي
إعداد الميزات الذكية
تدريب على الاستخدام
ضمان المصنع''',
                'icon': 'fa-magic',
                'is_featured': True,
                'order': 5
            },
            {
                'title': 'صيانة دورية',
                'title_en': 'Regular Maintenance',
                'category': maintenance_category,
                'short_description': 'صيانة دورية شاملة لأبواب الجراج',
                'description': 'خدمة الصيانة الدورية تشمل فحص شامل، تشحيم، ضبط، واختبار السلامة.',
                'features': '''فحص 20 نقطة
تشحيم جميع الأجزاء المتحركة
ضبط الزنبركات والكابلات
اختبار السلامة
تقرير مفصل''',
                'icon': 'fa-clipboard-check',
                'order': 6
            },
            {
                'title': 'استبدال اللوحات التالفة',
                'title_en': 'Panel Replacement',
                'category': repair_category,
                'short_description': 'استبدال اللوحات التالفة أو المخدوشة',
                'description': 'نستبدل اللوحات التالفة دون الحاجة لتغيير الباب بالكامل.',
                'features': '''مطابقة الألوان
لوحات أصلية
تركيب سريع
أسعار معقولة''',
                'icon': 'fa-square',
                'order': 7
            },
            {
                'title': 'برمجة جهاز التحكم عن بعد',
                'title_en': 'Remote Programming',
                'category': maintenance_category,
                'short_description': 'برمجة وإعداد أجهزة التحكم عن بعد',
                'description': 'برمجة أجهزة التحكم عن بعد والأكواد الرقمية (Keypads).',
                'features': '''برمجة سريعة
دعم جميع الأنواع
أجهزة تحكم إضافية متوفرة
خدمة في الموقع''',
                'icon': 'fa-remote-control',
                'order': 8
            },
        ]
        
        self.stdout.write('Creating services...')
        for service_data in services_data:
            service, created = Service.objects.get_or_create(
                title_en=service_data['title_en'],
                defaults=service_data
            )
            if created:
                self.stdout.write(f'  Created: {service.title}')
            else:
                self.stdout.write(f'  Already exists: {service.title}')
        
        self.stdout.write(self.style.SUCCESS('\nAll services created successfully!'))
        self.stdout.write(f'Total categories: {ServiceCategory.objects.count()}')
        self.stdout.write(f'Total services: {Service.objects.count()}')

