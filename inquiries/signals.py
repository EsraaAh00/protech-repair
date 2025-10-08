# inquiries/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import ContactInquiry
from .utils import send_whatsapp_notification, send_email_notification
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=ContactInquiry)
def notify_on_new_inquiry(sender, instance, created, **kwargs):
    """
    إرسال إشعارات عند إنشاء استفسار جديد
    Send notifications when a new inquiry is created
    """
    if created:
        logger.info(f"New inquiry created: {instance.id} - {instance.name}")
        
        # Send WhatsApp notification
        try:
            send_whatsapp_notification(instance)
        except Exception as e:
            logger.error(f"Error sending WhatsApp for inquiry {instance.id}: {str(e)}")
        
        # Send Email notification
        try:
            send_email_notification(instance)
        except Exception as e:
            logger.error(f"Error sending email for inquiry {instance.id}: {str(e)}")

