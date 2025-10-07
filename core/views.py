from django.shortcuts import render
from django.contrib.auth import get_user_model
from products.models import Product, Car, RealEstate
from categories.models import Category

User = get_user_model()

def home_view(request):
    """صفحة الرئيسية مع الإحصائيات والمنتجات المميزة"""
    
    # المنتجات المميزة (آخر 8 منتجات معتمدة)
    featured_products = Product.objects.filter(
        status='active', 
        is_approved=True
    ).select_related('seller', 'category').prefetch_related('images')[:8]
    
    # الإحصائيات
    total_products = Product.objects.filter(status='active', is_approved=True).count()
    total_users = User.objects.count()
    total_cars = Product.objects.filter(
        status='active', 
        is_approved=True,
        category__slug='cars'
    ).count()
    total_properties = Product.objects.filter(
        status='active', 
        is_approved=True,
        category__slug='real-estate'
    ).count()
    
    # أحدث السيارات
    latest_cars = Product.objects.filter(
        status='active',
        is_approved=True,
        category__slug='cars'
    ).select_related('seller').prefetch_related('images')[:3]
    
    # أحدث العقارات
    latest_properties = Product.objects.filter(
        status='active',
        is_approved=True,
        category__slug='real-estate'
    ).select_related('seller').prefetch_related('images')[:3]
    
    context = {
        'featured_products': featured_products,
        'total_products': total_products,
        'total_users': total_users,
        'total_cars': total_cars,
        'total_properties': total_properties,
        'latest_cars': latest_cars,
        'latest_properties': latest_properties,
    }
    
    return render(request, 'home.html', context) 