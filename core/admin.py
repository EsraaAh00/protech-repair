# core/admin.py
from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path
from django.contrib.admin import AdminSite
from django.utils.html import format_html
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from products.models import Product, ProductCategory
from services.models import Service, ServiceCategory
from inquiries.models import ContactInquiry
from django.contrib.auth import get_user_model

User = get_user_model()


class ProtechAdminSite(AdminSite):
    """
    لوحة تحكم مخصصة لشركة أبواب الجراج
    Custom admin site for Garage Door Company
    """
    site_header = "ProTech Garage Doors - Administration"
    site_title = "ProTech - Control Panel"
    index_title = "Welcome to ProTech Control Panel"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('statistics/', self.admin_view(self.statistics_view), name='admin_statistics'),
        ]
        return custom_urls + urls
    
    def statistics_view(self, request):
        """
        صفحة الإحصائيات
        Statistics page
        """
        # Product Statistics
        total_products = Product.objects.count()
        active_products = Product.objects.filter(is_active=True).count()
        featured_products = Product.objects.filter(is_featured=True).count()
        
        # Service Statistics
        total_services = Service.objects.count()
        active_services = Service.objects.filter(is_active=True).count()
        featured_services = Service.objects.filter(is_featured=True).count()
        
        # Inquiry Statistics
        total_inquiries = ContactInquiry.objects.count()
        new_inquiries = ContactInquiry.objects.filter(status='new').count()
        pending_inquiries = ContactInquiry.objects.filter(
            status__in=['new', 'contacted', 'in_progress']
        ).count()
        completed_inquiries = ContactInquiry.objects.filter(status='completed').count()
        
        # Weekly Statistics
        week_ago = timezone.now() - timedelta(days=7)
        new_inquiries_week = ContactInquiry.objects.filter(
            created_at__gte=week_ago
        ).count()
        
        # Popular Products
        popular_products = Product.objects.filter(
            is_active=True
        ).order_by('-views_count')[:5]
        
        # Recent Inquiries
        recent_inquiries = ContactInquiry.objects.select_related(
            'service_needed', 'product_interest'
        ).order_by('-created_at')[:10]
        
        # Category Statistics
        product_category_stats = ProductCategory.objects.annotate(
            products_count=Count('products'),
            active_products=Count('products', filter=Q(products__is_active=True))
        ).order_by('-products_count')
        
        service_category_stats = ServiceCategory.objects.annotate(
            services_count=Count('services'),
            active_services=Count('services', filter=Q(services__is_active=True))
        ).order_by('-services_count')
        
        context = {
            'total_products': total_products,
            'active_products': active_products,
            'featured_products': featured_products,
            'total_services': total_services,
            'active_services': active_services,
            'featured_services': featured_services,
            'total_inquiries': total_inquiries,
            'new_inquiries': new_inquiries,
            'pending_inquiries': pending_inquiries,
            'completed_inquiries': completed_inquiries,
            'new_inquiries_week': new_inquiries_week,
            'popular_products': popular_products,
            'recent_inquiries': recent_inquiries,
            'product_category_stats': product_category_stats,
            'service_category_stats': service_category_stats,
            'title': 'Site Statistics',
            'site_title': self.site_title,
            'site_header': self.site_header,
        }
        
        return TemplateResponse(request, 'admin/statistics.html', context)
    
    def index(self, request, extra_context=None):
        """
        الصفحة الرئيسية للوحة التحكم
        Admin dashboard homepage
        """
        extra_context = extra_context or {}
        
        # Quick Statistics
        quick_stats = {
            'total_products': Product.objects.filter(is_active=True).count(),
            'total_services': Service.objects.filter(is_active=True).count(),
            'new_inquiries': ContactInquiry.objects.filter(status='new').count(),
            'pending_inquiries': ContactInquiry.objects.filter(
                status__in=['contacted', 'in_progress']
            ).count(),
        }
        
        # Recent Inquiries needing attention
        pending_inquiries = ContactInquiry.objects.filter(
            status__in=['new', 'contacted']
        ).select_related('service_needed', 'product_interest').order_by('-created_at')[:5]
        
        # Recent Products
        recent_products = Product.objects.filter(
            is_active=True
        ).select_related('category').order_by('-created_at')[:5]
        
        extra_context.update({
            'quick_stats': quick_stats,
            'pending_inquiries': pending_inquiries,
            'recent_products': recent_products,
        })
        
        return super().index(request, extra_context)


# Use custom admin site
admin_site = ProtechAdminSite(name='protech_admin')

# Register models with custom admin site
from products.admin import (
    ProductAdmin, ProductCategoryAdmin, ProductImageAdmin,
    OpenerSpecificationsAdmin, DoorSpecificationsAdmin
)
from services.admin import ServiceAdmin, ServiceCategoryAdmin, ServiceImageAdmin
from inquiries.admin import ContactInquiryAdmin, InquiryNoteAdmin, InquiryAttachmentAdmin
from users.admin import CustomUserAdmin

# Register Products
admin_site.register(Product, ProductAdmin)
admin_site.register(ProductCategory, ProductCategoryAdmin)

# Register Services
admin_site.register(Service, ServiceAdmin)
admin_site.register(ServiceCategory, ServiceCategoryAdmin)

# Register Inquiries
admin_site.register(ContactInquiry, ContactInquiryAdmin)

# Register Users
admin_site.register(User, CustomUserAdmin)
