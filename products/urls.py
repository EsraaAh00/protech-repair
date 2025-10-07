# products/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.ProductListView.as_view(), name='list'),
    path('add/', views.AddProductView.as_view(), name='add'),
    path('simple-add/', views.SimpleAddProductView.as_view(), name='simple_add'),  # للاختبار
    path('debug/', views.debug_form_view, name='debug'),  # للتشخيص
    path('<int:pk>/', views.ProductDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.EditProductView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.DeleteProductView.as_view(), name='delete'),
    path('image/<int:image_id>/delete/', views.delete_product_image, name='delete_image'),  # حذف الصور
    path('my-products/', views.MyProductsView.as_view(), name='my_products'),
    path('search/', views.ProductSearchView.as_view(), name='search'),
    path('map/', views.ProductMapView.as_view(), name='map'),  # عرض المنتجات على الخريطة
    path('cars/', views.CarsListView.as_view(), name='cars'),
    path('real-estate/', views.RealEstateListView.as_view(), name='real_estate'),
    path('hotels/', views.HotelsListView.as_view(), name='hotels'),
]

