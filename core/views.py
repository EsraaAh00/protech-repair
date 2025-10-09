# core/views.py
from django.shortcuts import render
from django.contrib.auth import get_user_model
from products.models import Product, ProductCategory
from services.models import Service, ServiceCategory
from inquiries.models import RecentWork, ContactInquiry
from inquiries.forms import QuickContactForm

User = get_user_model()


def home_view(request):
    """
    Homepage - Garage Door Company
    """
    
    # Initialize form for display
    form = QuickContactForm()
    
    # Service Categories with Services
    service_categories = ServiceCategory.objects.filter(
        is_active=True
    ).prefetch_related('services')[:4]
    
    # All active services for display
    all_services = Service.objects.filter(
        is_active=True
    ).select_related('category')[:6]
    
    # Openers Products
    openers = Product.objects.filter(
        is_active=True,
        product_type='opener'
    ).select_related('category')[:4]
    
    # Door Products (first 4 for home display)
    doors = Product.objects.filter(
        is_active=True,
        product_type='door'
    ).select_related('category')[:4]
    
    # Recent Work with Reviews (latest 6 projects for slider)
    recent_works = RecentWork.objects.filter(
        is_active=True
    ).select_related('service').prefetch_related('reviews')[:6]
    
    # Statistics for About section
    total_customers = ContactInquiry.objects.filter(
        status='completed'
    ).count()
    
    # If no data, use default values
    if total_customers == 0:
        total_customers = 5000
    
    context = {
        'service_categories': service_categories,
        'all_services': all_services,
        'openers': openers,
        'doors': doors,
        'recent_works': recent_works,
        'total_customers': total_customers,
        'quick_contact_form': form,
    }
    
    return render(request, 'home.html', context)
