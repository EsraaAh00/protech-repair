# core/views.py
from django.shortcuts import render
from django.contrib.auth import get_user_model
from products.models import Product, ProductCategory
from services.models import Service, ServiceCategory
from inquiries.forms import QuickContactForm

User = get_user_model()


def home_view(request):
    """
    صفحة الرئيسية - شركة أبواب الجراج
    Homepage - Garage Door Company
    """
    
    # Featured Products (مميزة)
    featured_products = Product.objects.filter(
        is_active=True,
        is_featured=True
    ).select_related('category')[:6]
    
    # Best Seller Products (الأكثر مبيعاً)
    bestseller_products = Product.objects.filter(
        is_active=True,
        is_best_seller=True
    ).select_related('category')[:4]
    
    # Featured Services (خدمات مميزة)
    featured_services = Service.objects.filter(
        is_active=True,
        is_featured=True
    ).select_related('category')[:6]
    
    # All Services for display
    all_services = Service.objects.filter(is_active=True)[:8]
    
    # Product Categories
    product_categories = ProductCategory.objects.filter(is_active=True)[:4]
    
    # Service Categories
    service_categories = ServiceCategory.objects.filter(is_active=True)[:4]
    
    # Statistics
    total_products = Product.objects.filter(is_active=True).count()
    total_services = Service.objects.filter(is_active=True).count()
    
    # Quick Contact Form
    quick_contact_form = QuickContactForm()
    
    context = {
        'featured_products': featured_products,
        'bestseller_products': bestseller_products,
        'featured_services': featured_services,
        'all_services': all_services,
        'product_categories': product_categories,
        'service_categories': service_categories,
        'total_products': total_products,
        'total_services': total_services,
        'quick_contact_form': quick_contact_form,
    }
    
    return render(request, 'home.html', context)
