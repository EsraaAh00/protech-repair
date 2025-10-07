# locations/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q
from .models import Location, ProductLocation, SavedLocation
from products.models import Product
import json

def get_locations_api(request):
    """API endpoint to get locations for AJAX requests"""
    parent_id = request.GET.get('parent_id')
    level = request.GET.get('level')
    
    locations = Location.objects.filter(is_active=True)
    
    if parent_id:
        locations = locations.filter(parent_id=parent_id)
    elif level:
        locations = locations.filter(level=level)
    
    locations_data = [
        {
            'id': loc.id,
            'name': loc.name,
            'latitude': float(loc.latitude),
            'longitude': float(loc.longitude),
            'level': loc.level
        }
        for loc in locations
    ]
    
    return JsonResponse({'locations': locations_data})

def search_locations(request):
    """Search locations by name"""
    query = request.GET.get('q', '')
    
    if len(query) < 2:
        return JsonResponse({'locations': []})
    
    locations = Location.objects.filter(
        Q(name__icontains=query) | Q(name_en__icontains=query),
        is_active=True
    )[:10]
    
    locations_data = [
        {
            'id': loc.id,
            'name': loc.name,
            'full_path': loc.get_full_path(),
            'latitude': float(loc.latitude),
            'longitude': float(loc.longitude)
        }
        for loc in locations
    ]
    
    return JsonResponse({'locations': locations_data})

@login_required
def save_location(request):
    """Save a location for the user"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # If setting as default, remove default from other locations
            if data.get('is_default'):
                SavedLocation.objects.filter(
                    user=request.user, 
                    is_default=True
                ).update(is_default=False)
            
            saved_location = SavedLocation.objects.create(
                user=request.user,
                name=data['name'],
                latitude=data['latitude'],
                longitude=data['longitude'],
                address=data['address'],
                is_default=data.get('is_default', False)
            )
            
            return JsonResponse({
                'success': True,
                'location': {
                    'id': saved_location.id,
                    'name': saved_location.name,
                    'address': saved_location.address
                }
            })
            
        except (KeyError, ValueError, json.JSONDecodeError):
            return JsonResponse({'success': False, 'error': 'بيانات غير صحيحة'})
    
    return JsonResponse({'success': False, 'error': 'طريقة غير مسموحة'})

@login_required
def my_locations(request):
    """Display user's saved locations"""
    saved_locations = SavedLocation.objects.filter(user=request.user)
    
    return render(request, 'locations/my_locations.html', {
        'saved_locations': saved_locations
    })

@login_required
def delete_saved_location(request, location_id):
    """Delete a saved location"""
    location = get_object_or_404(SavedLocation, id=location_id, user=request.user)
    
    if request.method == 'POST':
        location.delete()
        messages.success(request, 'تم حذف الموقع بنجاح')
        return redirect('locations:my_locations')
    
    return render(request, 'locations/delete_location.html', {
        'location': location
    })

def product_map_view(request, product_id):
    """Display product location on map"""
    product = get_object_or_404(Product, id=product_id)
    
    # Get product location details
    location_details = None
    if hasattr(product, 'location_details'):
        location_details = product.location_details
    
    # Get nearby products (within 10km radius approximately)
    nearby_products = []
    if product.location_latitude and product.location_longitude:
        # Simple distance calculation (not precise but good for demo)
        lat_range = 0.1  # approximately 10km
        lng_range = 0.1
        
        nearby_products = Product.objects.filter(
            location_latitude__range=[
                product.location_latitude - lat_range,
                product.location_latitude + lat_range
            ],
            location_longitude__range=[
                product.location_longitude - lng_range,
                product.location_longitude + lng_range
            ],
            is_approved=True,
            status='active'
        ).exclude(id=product.id)[:10]
    
    return render(request, 'locations/product_map.html', {
        'product': product,
        'location_details': location_details,
        'nearby_products': nearby_products
    })

def area_products_map(request):
    """Display all products in a specific area on map"""
    # Get filter parameters
    location_id = request.GET.get('location')
    category_id = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    # Base query
    products = Product.objects.filter(
        is_approved=True,
        status='active',
        location_latitude__isnull=False,
        location_longitude__isnull=False
    )
    
    # Apply filters
    if location_id:
        location = get_object_or_404(Location, id=location_id)
        # Filter products in this location (simplified)
        products = products.filter(location_details__location=location)
    
    if category_id:
        products = products.filter(category_id=category_id)
    
    if min_price:
        products = products.filter(price__gte=min_price)
    
    if max_price:
        products = products.filter(price__lte=max_price)
    
    # Limit results for performance
    products = products[:100]
    
    # Prepare data for map
    products_data = []
    for product in products:
        products_data.append({
            'id': product.id,
            'title': product.title,
            'price': float(product.price),
            'latitude': float(product.location_latitude),
            'longitude': float(product.location_longitude),
            'image': product.images.first().image.url if product.images.first() else None,
            'url': f'/products/{product.id}/'
        })
    
    return render(request, 'locations/area_map.html', {
        'products_data': json.dumps(products_data),
        'total_products': len(products_data)
    })

