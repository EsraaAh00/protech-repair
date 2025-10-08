# products/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Product, ProductCategory, ProductImage, OpenerSpecifications, DoorSpecifications


class ProductListView(ListView):
    """
    عرض قائمة المنتجات
    Product list view
    """
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True).select_related('category')
        
        # Filter by category
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Filter by product type
        product_type = self.request.GET.get('type')
        if product_type:
            queryset = queryset.filter(product_type=product_type)
        
        # Search
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(name_en__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(model_number__icontains=search_query) |
                Q(brand__icontains=search_query)
            )
        
        # Sort
        sort_by = self.request.GET.get('sort', '-created_at')
        queryset = queryset.order_by(sort_by)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ProductCategory.objects.filter(is_active=True)
        
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            context['current_category'] = get_object_or_404(ProductCategory, slug=category_slug)
        
        return context


class ProductDetailView(DetailView):
    """
    عرض تفاصيل المنتج
    Product detail view
    """
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related('category').prefetch_related('images')
    
    def get_object(self):
        product = super().get_object()
        # Increment views count
        product.views_count += 1
        product.save(update_fields=['views_count'])
        return product
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        
        # Add specifications based on product type
        if product.product_type == 'opener':
            context['opener_specs'] = getattr(product, 'opener_specs', None)
        elif product.product_type == 'door':
            context['door_specs'] = getattr(product, 'door_specs', None)
        
        # Add related products
        related_products = Product.objects.filter(
            category=product.category,
            is_active=True
        ).exclude(id=product.id).select_related('category')[:4]
        
        context['related_products'] = related_products
        
        return context


def product_list(request, category_slug=None):
    """
    Function-based view for product listing
    """
    products = Product.objects.filter(is_active=True).select_related('category')
    categories = ProductCategory.objects.filter(is_active=True)
    current_category = None
    
    if category_slug:
        current_category = get_object_or_404(ProductCategory, slug=category_slug, is_active=True)
        products = products.filter(category=current_category)
    
    # Filter by type
    product_type = request.GET.get('type')
    if product_type:
        products = products.filter(product_type=product_type)
    
    # Search
    search_query = request.GET.get('q')
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(name_en__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(model_number__icontains=search_query)
        )
    
    context = {
        'products': products,
        'categories': categories,
        'current_category': current_category,
        'search_query': search_query,
    }
    
    return render(request, 'products/product_list.html', context)


def product_detail(request, slug):
    """
    Function-based view for product details
    """
    product = get_object_or_404(
        Product.objects.select_related('category').prefetch_related('images'),
        slug=slug,
        is_active=True
    )
    
    # Increment views
    product.views_count += 1
    product.save(update_fields=['views_count'])
    
    # Get specifications
    opener_specs = None
    door_specs = None
    
    if product.product_type == 'opener':
        opener_specs = getattr(product, 'opener_specs', None)
    elif product.product_type == 'door':
        door_specs = getattr(product, 'door_specs', None)
    
    # Related products
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'opener_specs': opener_specs,
        'door_specs': door_specs,
        'related_products': related_products,
    }
    
    return render(request, 'products/product_detail.html', context)


def openers_view(request):
    """
    عرض صفحة الفتاحات فقط
    Openers page view
    """
    openers = Product.objects.filter(
        is_active=True,
        product_type='opener'
    ).select_related('category').prefetch_related('images')
    
    # Get featured openers
    featured_openers = openers.filter(is_featured=True)[:6]
    
    context = {
        'products': openers,
        'featured_openers': featured_openers,
        'page_title': 'Garage Door Openers',
        'page_description': 'Browse our selection of garage door openers'
    }
    
    return render(request, 'products/openers.html', context)


def doors_view(request):
    """
    عرض صفحة الأبواب فقط
    Doors page view
    """
    doors = Product.objects.filter(
        is_active=True,
        product_type='door'
    ).select_related('category').prefetch_related('images')
    
    # Get featured doors
    featured_doors = doors.filter(is_featured=True)[:6]
    
    context = {
        'products': doors,
        'featured_doors': featured_doors,
        'page_title': 'Garage Doors',
        'page_description': 'Browse our selection of garage doors'
    }
    
    return render(request, 'products/doors.html', context)
