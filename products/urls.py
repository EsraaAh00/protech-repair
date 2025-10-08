# products/urls.py
from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # List views
    path('', views.product_list, name='product_list'),
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    
    # Special pages
    path('openers/', views.openers_view, name='openers'),
    path('doors/', views.doors_view, name='doors'),
    
    # Detail view
    path('<slug:slug>/', views.product_detail, name='product_detail'),
]
