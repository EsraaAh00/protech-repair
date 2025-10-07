from django.apps import AppConfig


class MessagingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'messaging'
    verbose_name = 'المحادثات والرسائل'
    
    def ready(self):
        import messaging.admin
