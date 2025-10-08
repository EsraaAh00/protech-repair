# inquiries/models.py
from django.db import models
from services.models import Service
from products.models import Product


class ContactInquiry(models.Model):
    """
    استفسارات وطلبات العملاء
    Customer inquiries and service requests
    """
    INQUIRY_TYPE_CHOICES = [
        ('free_estimate', 'تقدير مجاني / Free Estimate'),
        ('service_request', 'طلب خدمة / Service Request'),
        ('product_info', 'استفسار عن منتج / Product Info'),
        ('general', 'استفسار عام / General Inquiry'),
        ('emergency', 'حالة طارئة / Emergency'),
    ]
    
    STATUS_CHOICES = [
        ('new', 'جديد / New'),
        ('contacted', 'تم التواصل / Contacted'),
        ('in_progress', 'قيد المعالجة / In Progress'),
        ('completed', 'مكتمل / Completed'),
        ('cancelled', 'ملغي / Cancelled'),
    ]
    
    # Customer information
    name = models.CharField(max_length=200, verbose_name="الاسم")
    email = models.EmailField(blank=True, verbose_name="البريد الإلكتروني")
    phone = models.CharField(max_length=20, verbose_name="رقم الهاتف")
    address = models.CharField(max_length=500, blank=True, verbose_name="العنوان")
    
    # Inquiry details
    inquiry_type = models.CharField(
        max_length=20,
        choices=INQUIRY_TYPE_CHOICES,
        default='general',
        verbose_name="نوع الاستفسار"
    )
    service_needed = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inquiries',
        verbose_name="الخدمة المطلوبة"
    )
    product_interest = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inquiries',
        verbose_name="المنتج المهتم به"
    )
    message = models.TextField(verbose_name="الرسالة")
    
    # Status and tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name="الحالة"
    )
    
    # WhatsApp notification
    whatsapp_sent = models.BooleanField(default=False, verbose_name="تم إرسال واتساب")
    whatsapp_sent_at = models.DateTimeField(null=True, blank=True, verbose_name="وقت إرسال واتساب")
    whatsapp_error = models.TextField(blank=True, verbose_name="خطأ واتساب")
    
    # Admin notes
    admin_notes = models.TextField(blank=True, verbose_name="ملاحظات الإدارة")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")
    contacted_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ التواصل")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الإكمال")
    
    # IP and User Agent for spam prevention
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="عنوان IP")
    user_agent = models.CharField(max_length=500, blank=True, verbose_name="User Agent")
    
    class Meta:
        verbose_name = "استفسار"
        verbose_name_plural = "الاستفسارات"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['inquiry_type']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.get_inquiry_type_display()} - {self.created_at.strftime('%Y-%m-%d')}"
    
    def get_whatsapp_message(self):
        """
        تنسيق رسالة واتساب
        Format WhatsApp message
        """
        message_parts = [
            "🔔 *طلب جديد / New Inquiry*",
            "",
            f"*الاسم / Name:* {self.name}",
            f"*الهاتف / Phone:* {self.phone}",
        ]
        
        if self.email:
            message_parts.append(f"*البريد / Email:* {self.email}")
        
        if self.address:
            message_parts.append(f"*العنوان / Address:* {self.address}")
        
        message_parts.append("")
        message_parts.append(f"*نوع الطلب / Type:* {self.get_inquiry_type_display()}")
        
        if self.service_needed:
            message_parts.append(f"*الخدمة / Service:* {self.service_needed.title}")
        
        if self.product_interest:
            message_parts.append(f"*المنتج / Product:* {self.product_interest.name}")
        
        message_parts.append("")
        message_parts.append(f"*الرسالة / Message:*")
        message_parts.append(self.message)
        
        message_parts.append("")
        message_parts.append(f"_التاريخ / Date: {self.created_at.strftime('%Y-%m-%d %H:%M')}_")
        
        return "\n".join(message_parts)


class InquiryNote(models.Model):
    """
    ملاحظات على الاستفسارات
    Notes on inquiries for tracking
    """
    inquiry = models.ForeignKey(
        ContactInquiry,
        on_delete=models.CASCADE,
        related_name='notes',
        verbose_name="الاستفسار"
    )
    note = models.TextField(verbose_name="الملاحظة")
    created_by = models.CharField(max_length=100, blank=True, verbose_name="أنشأها")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    
    class Meta:
        verbose_name = "ملاحظة"
        verbose_name_plural = "الملاحظات"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Note for {self.inquiry.name} - {self.created_at.strftime('%Y-%m-%d')}"


class InquiryAttachment(models.Model):
    """
    مرفقات الاستفسارات (صور أو ملفات من العميل)
    Inquiry attachments (images or files from customer)
    """
    inquiry = models.ForeignKey(
        ContactInquiry,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name="الاستفسار"
    )
    file = models.FileField(upload_to='inquiry_attachments/', verbose_name="الملف")
    description = models.CharField(max_length=200, blank=True, verbose_name="الوصف")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الرفع")
    
    class Meta:
        verbose_name = "مرفق"
        verbose_name_plural = "المرفقات"
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"Attachment for {self.inquiry.name}"
