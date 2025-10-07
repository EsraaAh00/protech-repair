# admin_panel/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.admin_dashboard, name='dashboard'),
    path('products/pending/', views.pending_products, name='pending_products'),
    path('products/<int:product_id>/approve/', views.approve_product, name='approve_product'),
    path('products/<int:product_id>/reject/', views.reject_product, name='reject_product'),
    path('products/<int:product_id>/', views.product_detail_admin, name='product_detail'),
    path('users/', views.users_management, name='users_management'),
    path('users/<int:user_id>/verify/', views.verify_user, name='verify_user'),
    path('users/<int:user_id>/suspend/', views.suspend_user, name='suspend_user'),
    path('reports/', views.reports_analytics, name='reports'),
    path('settings/', views.system_settings, name='settings'),
    path('bulk-actions/', views.bulk_actions, name='bulk_actions'),
]

