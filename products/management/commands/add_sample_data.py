from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from products.models import Product
from orders.models import Order
from reviews.models import Review
from decimal import Decimal
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'إضافة بيانات تجريبية للطلبات والتقييمات'

    def handle(self, *args, **options):
        # التأكد من وجود مستخدمين ومنتجات
        users = User.objects.all()
        products = Product.objects.filter(status='active', is_approved=True)
        
        if users.count() < 2:
            self.stdout.write(self.style.ERROR('يجب وجود مستخدمين على الأقل'))
            return
            
        if products.count() < 1:
            self.stdout.write(self.style.ERROR('يجب وجود منتجات على الأقل'))
            return

        # إنشاء مستخدمين إضافيين
        test_users = []
        for i in range(3):
            user, created = User.objects.get_or_create(
                username=f'test_user_{i+1}',
                defaults={
                    'email': f'test{i+1}@example.com',
                    'first_name': ['أحمد', 'فاطمة', 'محمد'][i],
                    'last_name': ['العلي', 'السالم', 'الأحمد'][i],
                    'is_seller': i % 2 == 0
                }
            )
            if created:
                user.set_password('test123')
                user.save()
                test_users.append(user)

        all_users = list(users) + test_users
        
        # إضافة طلبات
        orders_created = 0
        
        for product in products[:6]:
            buyer = random.choice([u for u in all_users if u != product.seller])
            
            amount_variation = random.uniform(0.9, 1.1)
            total_amount = Decimal(str(float(product.price) * amount_variation))
            
            order = Order.objects.create(
                product=product,
                buyer=buyer,
                seller=product.seller,
                total_amount=total_amount,
                status=random.choice(['pending', 'confirmed', 'completed', 'cancelled']),
                notes=random.choice([
                    'أرجو التسليم في أسرع وقت ممكن',
                    'يرجى التأكد من حالة المنتج قبل التسليم',
                    'موافق على الشروط والأحكام',
                    ''
                ])
            )
            orders_created += 1

        # إضافة تقييمات
        reviews_created = 0
        
        for product in products[:4]:
            reviewer = random.choice([u for u in all_users if u != product.seller])
            
            Review.objects.create(
                reviewer=reviewer,
                product=product,
                seller=product.seller,
                rating=random.randint(3, 5),
                comment=random.choice([
                    'منتج ممتاز وبائع محترم، أنصح بالتعامل معه',
                    'حالة المنتج كما هو موصوف تماماً، شكراً لك',
                    'تسليم سريع وتعامل راقي، تجربة رائعة',
                    'منتج جيد لكن التسليم تأخر قليلاً',
                    'راضي عن الشراء، المنتج يستحق السعر'
                ])
            )
            reviews_created += 1

        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('تم إنشاء البيانات التجريبية بنجاح!'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS(f'🛒 الطلبات: {orders_created}'))
        self.stdout.write(self.style.SUCCESS(f'⭐ التقييمات: {reviews_created}'))
        self.stdout.write(self.style.SUCCESS('=' * 50)) 