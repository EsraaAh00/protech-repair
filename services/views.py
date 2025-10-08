# services/views.py
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Service, ServiceCategory


class ServiceListView(ListView):
    """
    عرض قائمة الخدمات
    Display list of services
    """
    model = Service
    template_name = 'services/service_list.html'
    context_object_name = 'services'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Service.objects.filter(is_active=True).select_related('category')
        
        # Filter by category if provided
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ServiceCategory.objects.filter(is_active=True)
        
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            context['current_category'] = get_object_or_404(ServiceCategory, slug=category_slug)
        
        return context


class ServiceDetailView(DetailView):
    """
    عرض تفاصيل الخدمة
    Display service details
    """
    model = Service
    template_name = 'services/service_detail.html'
    context_object_name = 'service'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        return Service.objects.filter(is_active=True).select_related('category').prefetch_related('images')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get related services from the same category
        context['related_services'] = Service.objects.filter(
            category=self.object.category,
            is_active=True
        ).exclude(id=self.object.id)[:3]
        return context


def service_list(request, category_slug=None):
    """
    Function-based view for service listing
    """
    services = Service.objects.filter(is_active=True).select_related('category')
    categories = ServiceCategory.objects.filter(is_active=True)
    current_category = None
    
    if category_slug:
        current_category = get_object_or_404(ServiceCategory, slug=category_slug, is_active=True)
        services = services.filter(category=current_category)
    
    context = {
        'services': services,
        'categories': categories,
        'current_category': current_category,
    }
    return render(request, 'services/service_list.html', context)


def service_detail(request, slug):
    """
    Function-based view for service details
    """
    service = get_object_or_404(Service, slug=slug, is_active=True)
    related_services = Service.objects.filter(
        category=service.category,
        is_active=True
    ).exclude(id=service.id)[:3]
    
    context = {
        'service': service,
        'related_services': related_services,
    }
    return render(request, 'services/service_detail.html', context)
