from django.core.management.base import BaseCommand
from categories.models import Category

class Command(BaseCommand):
    help = 'إنشاء الفئات الأساسية للموقع'

    def handle(self, *args, **options):
        categories_data = [
            {
                'name': 'السيارات',
                'slug': 'cars',
                'subcategories': [
                    {'name': 'سيارات جديدة', 'slug': 'new-cars'},
                    {'name': 'سيارات مستعملة', 'slug': 'used-cars'},
                    {'name': 'شاحنات', 'slug': 'trucks'},
                    {'name': 'دراجات نارية', 'slug': 'motorcycles'},
                ]
            },
            {
                'name': 'العقارات',
                'slug': 'real-estate',
                'subcategories': [
                    {'name': 'شقق للبيع', 'slug': 'apartments-for-sale'},
                    {'name': 'شقق للإيجار', 'slug': 'apartments-for-rent'},
                    {'name': 'فلل للبيع', 'slug': 'villas-for-sale'},
                    {'name': 'فلل للإيجار', 'slug': 'villas-for-rent'},
                    {'name': 'أراضي', 'slug': 'lands'},
                    {'name': 'محلات تجارية', 'slug': 'commercial'},
                ]
            },
            {
                'name': 'الفنادق',
                'slug': 'hotels',
                'subcategories': [
                    {'name': 'فنادق 5 نجوم', 'slug': 'five-star-hotels'},
                    {'name': 'فنادق 4 نجوم', 'slug': 'four-star-hotels'},
                    {'name': 'فنادق 3 نجوم', 'slug': 'three-star-hotels'},
                    {'name': 'شقق مفروشة', 'slug': 'furnished-apartments'},
                    {'name': 'استراحات', 'slug': 'resorts'},
                ]
            },
        ]

        for category_data in categories_data:
            # إنشاء الفئة الرئيسية
            parent_category, created = Category.objects.get_or_create(
                slug=category_data['slug'],
                defaults={'name': category_data['name']}
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'تم إنشاء الفئة: {parent_category.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'الفئة موجودة بالفعل: {parent_category.name}')
                )

            # إنشاء الفئات الفرعية
            for subcategory_data in category_data['subcategories']:
                subcategory, created = Category.objects.get_or_create(
                    slug=subcategory_data['slug'],
                    defaults={
                        'name': subcategory_data['name'],
                        'parent': parent_category
                    }
                )
                
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'  └── تم إنشاء الفئة الفرعية: {subcategory.name}')
                    )

        self.stdout.write(
            self.style.SUCCESS('تم إنشاء جميع الفئات بنجاح!')
        ) 