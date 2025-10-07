# dalal_saudi/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from . import views

app_name = 'locations'

urlpatterns = [
    path('api/locations/', views.get_locations_api, name='locations_api'),
    path('api/search/', views.search_locations, name='search_locations'),
    path('save/', views.save_location, name='save_location'),
    path('my-locations/', views.my_locations, name='my_locations'),
    path('delete/<int:location_id>/', views.delete_saved_location, name='delete_location'),
    path('map/product/<int:product_id>/', views.product_map_view, name='product_map'),
    path('map/area/', views.area_products_map, name='area_map'),
]

