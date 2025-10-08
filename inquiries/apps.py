# inquiries/apps.py
from django.apps import AppConfig


class InquiriesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inquiries'
    verbose_name = 'الاستفسارات'
    
    def ready(self):
        import inquiries.signals
