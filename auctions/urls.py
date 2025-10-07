# dalal_saudi/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from . import views

app_name = 'auctions'

urlpatterns = [
    path('', views.auction_list, name='list'),
    path('<int:auction_id>/', views.auction_detail, name='detail'),
    path('create/<int:product_id>/', views.create_auction, name='create'),
    path('bid/<int:auction_id>/', views.place_bid, name='place_bid'),
    path('my-auctions/', views.my_auctions, name='my_auctions'),
    path('cancel/<int:auction_id>/', views.cancel_auction, name='cancel'),
]

