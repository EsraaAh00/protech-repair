# dalal_saudi/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from . import views

app_name = 'orders'

urlpatterns = [
    path('my-orders/', views.my_orders, name='my_orders'),
    path('<int:order_id>/', views.order_detail, name='detail'),
    path('create/<int:product_id>/', views.create_order, name='create'),
    path('update-status/<int:order_id>/', views.update_order_status, name='update_status'),
    path('cancel/<int:order_id>/', views.cancel_order, name='cancel'),
    path('history/', views.order_history, name='history'),
]

