# services/urls.py
from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    path('', views.service_list, name='service_list'),
    path('category/<slug:category_slug>/', views.service_list, name='service_list_by_category'),
    path('<slug:slug>/', views.service_detail, name='service_detail'),
]

