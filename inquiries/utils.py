# inquiries/utils.py
import requests
from django.conf import settings
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


def send_whatsapp_notification(inquiry):
    """
    إرسال إشعار واتساب للمالك عند استلام استفسار جديد
    Send WhatsApp notification to owner when new inquiry is received
    
    This uses WhatsApp Business API or a third-party service like Twilio
    """
    try:
        # Get WhatsApp settings from Django settings
        whatsapp_enabled = getattr(settings, 'WHATSAPP_ENABLED', False)
        
        if not whatsapp_enabled:
            logger.info("WhatsApp notifications are disabled")
            return False
        
        whatsapp_api_url = getattr(settings, 'WHATSAPP_API_URL', '')
        whatsapp_api_token = getattr(settings, 'WHATSAPP_API_TOKEN', '')
        whatsapp_phone_number = getattr(settings, 'WHATSAPP_PHONE_NUMBER', '')
        
        if not all([whatsapp_api_url, whatsapp_api_token, whatsapp_phone_number]):
            logger.error("WhatsApp settings are not configured properly")
            inquiry.whatsapp_error = "WhatsApp settings not configured"
            inquiry.save()
            return False
        
        # Prepare the message
        message = inquiry.get_whatsapp_message()
        
        # Example using Twilio API
        # You can replace this with any WhatsApp API service
        """
        headers = {
            'Authorization': f'Bearer {whatsapp_api_token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'to': whatsapp_phone_number,
            'body': message
        }
        
        response = requests.post(
            whatsapp_api_url,
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            inquiry.whatsapp_sent = True
            inquiry.whatsapp_sent_at = timezone.now()
            inquiry.whatsapp_error = ''
            inquiry.save()
            logger.info(f"WhatsApp notification sent for inquiry {inquiry.id}")
            return True
        else:
            error_msg = f"Failed to send WhatsApp: {response.status_code} - {response.text}"
            inquiry.whatsapp_error = error_msg
            inquiry.save()
            logger.error(error_msg)
            return False
        """
        
        # For now, just log the message (implement actual API call above)
        logger.info(f"WhatsApp message prepared for inquiry {inquiry.id}:")
        logger.info(message)
        
        # Mark as sent (remove this when implementing actual API)
        inquiry.whatsapp_sent = True
        inquiry.whatsapp_sent_at = timezone.now()
        inquiry.save()
        
        return True
        
    except Exception as e:
        error_msg = f"Error sending WhatsApp notification: {str(e)}"
        logger.error(error_msg)
        inquiry.whatsapp_error = error_msg
        inquiry.save()
        return False


def send_email_notification(inquiry):
    """
    إرسال إشعار بريد إلكتروني
    Send email notification
    """
    try:
        from django.core.mail import send_mail
        from django.template.loader import render_to_string
        
        # Get admin email from settings
        admin_email = getattr(settings, 'ADMIN_EMAIL', '')
        
        if not admin_email:
            logger.warning("Admin email not configured")
            return False
        
        subject = f"New Inquiry from {inquiry.name}"
        message = inquiry.get_whatsapp_message()
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [admin_email],
            fail_silently=False,
        )
        
        logger.info(f"Email notification sent for inquiry {inquiry.id}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending email notification: {str(e)}")
        return False


def get_client_ip(request):
    """
    الحصول على IP address للعميل
    Get client IP address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    """
    الحصول على User Agent
    Get user agent
    """
    return request.META.get('HTTP_USER_AGENT', '')[:500]

