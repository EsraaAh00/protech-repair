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
    name = models.CharField(max_length=200, verbose_name="Name")
    email = models.EmailField(blank=True, verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Phone")
    address = models.CharField(max_length=500, blank=True, verbose_name="Address")
    
    # Inquiry details
    inquiry_type = models.CharField(
        max_length=20,
        choices=INQUIRY_TYPE_CHOICES,
        default='general',
        verbose_name="Inquiry Type"
    )
    service_needed = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inquiries',
        verbose_name="Service Needed"
    )
    product_interest = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inquiries',
        verbose_name="Product Interest"
    )
    message = models.TextField(verbose_name="Message")
    
    # Status and tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name="Status"
    )
    
    # WhatsApp notification
    whatsapp_sent = models.BooleanField(default=False, verbose_name="WhatsApp Sent")
    whatsapp_sent_at = models.DateTimeField(null=True, blank=True, verbose_name="WhatsApp Sent At")
    whatsapp_error = models.TextField(blank=True, verbose_name="WhatsApp Error")
    
    # Admin notes
    admin_notes = models.TextField(blank=True, verbose_name="Admin Notes")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    contacted_at = models.DateTimeField(null=True, blank=True, verbose_name="Contacted At")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="Completed At")
    
    # IP and User Agent for spam prevention
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP Address")
    user_agent = models.CharField(max_length=500, blank=True, verbose_name="User Agent")
    
    class Meta:
        verbose_name = "Contact Inquiry"
        verbose_name_plural = "Contact Inquiries"
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
        verbose_name="Inquiry"
    )
    note = models.TextField(verbose_name="Note")
    created_by = models.CharField(max_length=100, blank=True, verbose_name="Created By")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    
    class Meta:
        verbose_name = "Inquiry Note"
        verbose_name_plural = "Inquiry Notes"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Note for {self.inquiry.name} - {self.created_at.strftime('%Y-%m-%d')}"


class RecentWork(models.Model):
    """
    Recent work portfolio/gallery
    عرض الأعمال السابقة
    """
    title = models.CharField(max_length=200, verbose_name="Project Title")
    image = models.ImageField(upload_to='recent_work/', verbose_name="Project Image")
    description = models.TextField(verbose_name="Project Description")
    
    # Display settings
    is_featured = models.BooleanField(default=False, verbose_name="Featured")
    order = models.IntegerField(default=0, verbose_name="Display Order")
    is_active = models.BooleanField(default=True, verbose_name="Active")
    
    # Related service (optional)
    service = models.ForeignKey(
        Service,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='recent_works',
        verbose_name="Related Service"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    
    class Meta:
        verbose_name = "Recent Work"
        verbose_name_plural = "Recent Works"
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return self.title
    
    def get_average_rating(self):
        """Calculate average rating from reviews"""
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            return reviews.aggregate(models.Avg('rating'))['rating__avg']
        return 0
    
    def get_total_reviews(self):
        """Get total approved reviews count"""
        return self.reviews.filter(is_approved=True).count()


class Review(models.Model):
    """
    Customer reviews and ratings for recent work
    تقييمات العملاء للأعمال
    """
    recent_work = models.ForeignKey(
        RecentWork,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name="Recent Work"
    )
    
    # Customer info
    customer_name = models.CharField(max_length=200, verbose_name="Customer Name")
    customer_email = models.EmailField(blank=True, verbose_name="Customer Email")
    
    # Review details
    rating = models.IntegerField(
        choices=[(i, f"{i} Stars") for i in range(1, 6)],
        verbose_name="Rating",
        help_text="1 to 5 stars"
    )
    review_text = models.TextField(verbose_name="Review Text")
    
    # Moderation
    is_approved = models.BooleanField(default=False, verbose_name="Approved")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    
    class Meta:
        verbose_name = "Review"
        verbose_name_plural = "Reviews"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.customer_name} - {self.rating} stars"
    
    def get_stars_display(self):
        """Return star icons for display"""
        return "⭐" * self.rating
