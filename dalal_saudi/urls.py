# dalal_saudi/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .admin import admin_site
from messaging.views import mark_messages_read_admin

urlpatterns = [
    path('admin/', admin_site.urls),
    path('admin/mark-messages-read/', mark_messages_read_admin, name='admin_mark_messages_read'),
    path('', views.home_view, name='home'),
    path('users/', include('users.urls', namespace='users')),
    path('products/', include('products.urls', namespace='products')),
    path('categories/', include('categories.urls', namespace='categories')),
    path('messaging/', include('messaging.urls', namespace='messaging')),
    path('auctions/', include('auctions.urls', namespace='auctions')),
    path('locations/', include('locations.urls', namespace='locations')),
    path('admin-panel/', include('admin_panel.urls', namespace='admin_panel')),
    path('reviews/', include('reviews.urls', namespace='reviews')),
    path('orders/', include('orders.urls', namespace='orders')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

