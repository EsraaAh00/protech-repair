# inquiries/urls.py
from django.urls import path
from . import views

app_name = 'inquiries'

urlpatterns = [
    path('contact/', views.contact_form_view, name='contact_form'),
    path('quick-contact/', views.quick_contact_view, name='quick_contact'),
    path('thank-you/', views.thank_you_view, name='thank_you'),
    path('<int:pk>/', views.inquiry_detail_view, name='inquiry_detail'),
]

