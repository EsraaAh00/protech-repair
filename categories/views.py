from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.db.models import Count, Q
from .models import Category
from products.models import Product

# Create your views here.

class CategoryListView(ListView):
    model = Category
    template_name = 'categories/list.html'
    context_object_name = 'categories'
    
    def get_queryset(self):
        return Category.objects.filter(parent=None).annotate(
            total_products=Count('products'),
            active_products=Count('products', filter=Q(products__status='active'))
        ).order_by('name')

class CategoryDetailView(DetailView):
    model = Category
    template_name = 'categories/detail.html'
    context_object_name = 'category'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_object()
        context['products'] = Product.objects.filter(
            category=category, 
            status='active'
        ).select_related('seller', 'category').prefetch_related('images')
        context['subcategories'] = category.subcategories.all()
        context['total_products'] = category.products.count()
        context['active_products'] = category.products.filter(status='active').count()
        return context
