# core/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .admin import admin_site

urlpatterns = [
    path('admin/', admin_site.urls),
    path('', views.home_view, name='home'),
    path('users/', include('users.urls', namespace='users')),
    path('products/', include('products.urls', namespace='products')),
    path('categories/', include('categories.urls', namespace='categories')),
    path('reviews/', include('reviews.urls', namespace='reviews')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('accounts/', include('django.contrib.auth.urls')),  # Default auth URLs
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

