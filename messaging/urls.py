# dalal_saudi/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from . import views

app_name = 'messaging'

urlpatterns = [
    path('', views.conversations_list, name='conversations_list'),
    path('inbox/', views.inbox, name='inbox'),
    path('conversation/<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    path('start/<int:product_id>/', views.start_conversation, name='start_conversation'),
    path('send-ajax/', views.send_message_ajax, name='send_message_ajax'),
    path('send-message/', views.send_message, name='send_message'),
    path('mark-as-read/', views.mark_as_read, name='mark_as_read'),
    path('admin/mark-messages-read/', views.mark_messages_read_admin, name='mark_messages_read_admin'),
]

