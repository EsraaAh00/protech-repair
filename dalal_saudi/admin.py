from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path
from django.contrib.admin import AdminSite
from django.utils.html import format_html
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from products.models import Product
from categories.models import Category
from django.contrib.auth import get_user_model

User = get_user_model()

class DalalSaudiAdminSite(AdminSite):
    site_header = "إدارة Dalal Alsaudia"
    site_title = "Dalal Alsaudia - لوحة التحكم"
    index_title = "مرحباً في لوحة التحكم الرئيسية"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('statistics/', self.admin_view(self.statistics_view), name='admin_statistics'),
        ]
        return custom_urls + urls
    
    def statistics_view(self, request):
        # إحصائيات عامة
        total_products = Product.objects.count()
        active_products = Product.objects.filter(status='active').count()
        pending_products = Product.objects.filter(status='pending_approval').count()
        sold_products = Product.objects.filter(status='sold').count()
        
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        new_users_week = User.objects.filter(
            date_joined__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        total_categories = Category.objects.count()
        
        # إحصائيات المبيعات
        total_revenue = Product.objects.filter(status='sold').aggregate(
            total=Sum('price')
        )['total'] or 0
        
        # المنتجات الأكثر مشاهدة
        popular_products = Product.objects.filter(
            status='active'
        ).order_by('-views_count')[:5]
        
        # المستخدمين الأكثر نشاطاً
        active_sellers = User.objects.annotate(
            products_count=Count('products')
        ).filter(products_count__gt=0).order_by('-products_count')[:5]
        
        # إحصائيات الفئات
        category_stats = Category.objects.annotate(
            products_count=Count('products'),
            active_products=Count('products', filter=Q(products__status='active'))
        ).order_by('-products_count')
        
        context = {
            'total_products': total_products,
            'active_products': active_products,
            'pending_products': pending_products,
            'sold_products': sold_products,
            'total_users': total_users,
            'active_users': active_users,
            'new_users_week': new_users_week,
            'total_categories': total_categories,
            'total_revenue': total_revenue,
            'popular_products': popular_products,
            'active_sellers': active_sellers,
            'category_stats': category_stats,
            'title': 'إحصائيات الموقع',
            'site_title': self.site_title,
            'site_header': self.site_header,
        }
        
        return TemplateResponse(request, 'admin/statistics.html', context)
    
    def index(self, request, extra_context=None):
        # إضافة إحصائيات سريعة للصفحة الرئيسية
        extra_context = extra_context or {}
        
        # إحصائيات سريعة
        quick_stats = {
            'total_products': Product.objects.count(),
            'pending_approval': Product.objects.filter(status='pending_approval').count(),
            'new_users_today': User.objects.filter(
                date_joined__date=timezone.now().date()
            ).count(),
            'total_revenue': Product.objects.filter(status='sold').aggregate(
                total=Sum('price')
            )['total'] or 0,
        }
        
        # المنتجات التي تحتاج مراجعة
        pending_products = Product.objects.filter(
            status='pending_approval'
        ).select_related('seller', 'category')[:5]
        
        # آخر المستخدمين المسجلين
        recent_users = User.objects.filter(
            is_active=True
        ).order_by('-date_joined')[:5]
        
        extra_context.update({
            'quick_stats': quick_stats,
            'pending_products': pending_products,
            'recent_users': recent_users,
        })
        
        return super().index(request, extra_context)

# استخدام الموقع المخصص
admin_site = DalalSaudiAdminSite(name='dalal_admin')

# تسجيل النماذج مع الموقع المخصص
from products.admin import ProductAdmin, CarAdmin, RealEstateAdmin, HotelBookingAdmin, ProductImageAdmin
from categories.admin import CategoryAdmin
from users.admin import CustomUserAdmin

# تسجيل النماذج الجديدة
from messaging.admin import MessageAdmin, ConversationAdmin
from orders.admin import OrderAdmin
from reviews.admin import ReviewAdmin
from auctions.admin import AuctionAdmin, BidAdmin

# تسجيل النماذج الأساسية
admin_site.register(Product, ProductAdmin)
admin_site.register(User, CustomUserAdmin)
admin_site.register(Category, CategoryAdmin)

# تسجيل النماذج الجديدة
from messaging.models import Message, Conversation
from orders.models import Order
from reviews.models import Review
from auctions.models import Auction, Bid

admin_site.register(Message, MessageAdmin)
admin_site.register(Conversation, ConversationAdmin)
admin_site.register(Order, OrderAdmin)
admin_site.register(Review, ReviewAdmin)
admin_site.register(Auction, AuctionAdmin)
admin_site.register(Bid, BidAdmin) 