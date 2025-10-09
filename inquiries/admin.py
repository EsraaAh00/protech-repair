# inquiries/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import ContactInquiry, InquiryNote, RecentWork, Review
from .utils import send_whatsapp_notification, send_email_notification


class InquiryNoteInline(admin.TabularInline):
    model = InquiryNote
    extra = 1
    fields = ['note', 'created_by', 'created_at']
    readonly_fields = ['created_at']


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    fields = ['customer_name', 'rating', 'review_text', 'is_approved', 'created_at']
    readonly_fields = ['created_at']


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'name', 'phone', 'inquiry_type', 
        'status_badge', 'whatsapp_status', 
        'created_at_formatted', 'action_buttons'
    ]
    list_filter = [
        'status', 'inquiry_type', 'whatsapp_sent',
        'created_at', 'service_needed', 'product_interest'
    ]
    search_fields = [
        'name', 'phone', 'email', 'address', 
        'message', 'admin_notes'
    ]
    readonly_fields = [
        'created_at', 'updated_at', 'whatsapp_sent_at',
        'ip_address', 'user_agent', 'whatsapp_message_preview'
    ]
    list_per_page = 25
    inlines = [InquiryNoteInline]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('معلومات العميل / Customer Info', {
            'fields': ('name', 'phone', 'email', 'address')
        }),
        ('تفاصيل الاستفسار / Inquiry Details', {
            'fields': (
                'inquiry_type', 'service_needed', 
                'product_interest', 'message'
            )
        }),
        ('الحالة / Status', {
            'fields': ('status', 'admin_notes')
        }),
        ('واتساب / WhatsApp', {
            'fields': (
                'whatsapp_sent', 'whatsapp_sent_at', 
                'whatsapp_error', 'whatsapp_message_preview'
            ),
            'classes': ('collapse',)
        }),
        ('معلومات إضافية / Additional Info', {
            'fields': (
                'ip_address', 'user_agent',
                'created_at', 'updated_at',
                'contacted_at', 'completed_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'service_needed', 'product_interest'
        )
    
    def status_badge(self, obj):
        """عرض الحالة بشكل ملون"""
        colors = {
            'new': '#dc3545',  # red
            'contacted': '#ffc107',  # yellow
            'in_progress': '#17a2b8',  # blue
            'completed': '#28a745',  # green
            'cancelled': '#6c757d',  # gray
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'الحالة / Status'
    
    def whatsapp_status(self, obj):
        """عرض حالة إرسال واتساب"""
        if obj.whatsapp_sent:
            return format_html(
                '<span style="color: green;">✓ تم الإرسال</span>'
            )
        elif obj.whatsapp_error:
            return format_html(
                '<span style="color: red;" title="{}">✗ خطأ</span>',
                obj.whatsapp_error
            )
        else:
            return format_html(
                '<span style="color: gray;">⊘ لم يرسل</span>'
            )
    whatsapp_status.short_description = 'واتساب'
    
    def created_at_formatted(self, obj):
        """تنسيق التاريخ"""
        return obj.created_at.strftime('%Y-%m-%d %H:%M')
    created_at_formatted.short_description = 'التاريخ / Date'
    created_at_formatted.admin_order_field = 'created_at'
    
    def action_buttons(self, obj):
        """أزرار الإجراءات"""
        return format_html(
            '<a class="button" href="/admin/inquiries/contactinquiry/{}/change/">عرض</a>',
            obj.pk
        )
    action_buttons.short_description = 'إجراءات'
    
    def whatsapp_message_preview(self, obj):
        """عرض نص رسالة واتساب"""
        return format_html(
            '<pre style="white-space: pre-wrap; background: #f5f5f5; padding: 10px; border-radius: 5px;">{}</pre>',
            obj.get_whatsapp_message()
        )
    whatsapp_message_preview.short_description = 'معاينة رسالة واتساب'
    
    # Actions
    actions = [
        'mark_as_contacted', 'mark_as_in_progress', 
        'mark_as_completed', 'resend_whatsapp'
    ]
    
    def mark_as_contacted(self, request, queryset):
        """تعيين الحالة كـ "تم التواصل" """
        count = queryset.update(
            status='contacted',
            contacted_at=timezone.now()
        )
        self.message_user(request, f"{count} استفسار تم تحديثه")
    mark_as_contacted.short_description = "تعيين كـ تم التواصل"
    
    def mark_as_in_progress(self, request, queryset):
        """تعيين الحالة كـ "قيد المعالجة" """
        count = queryset.update(status='in_progress')
        self.message_user(request, f"{count} استفسار تم تحديثه")
    mark_as_in_progress.short_description = "تعيين كـ قيد المعالجة"
    
    def mark_as_completed(self, request, queryset):
        """تعيين الحالة كـ "مكتمل" """
        count = queryset.update(
            status='completed',
            completed_at=timezone.now()
        )
        self.message_user(request, f"{count} استفسار تم إكماله")
    mark_as_completed.short_description = "تعيين كـ مكتمل"
    
    def resend_whatsapp(self, request, queryset):
        """إعادة إرسال إشعار واتساب"""
        success_count = 0
        for inquiry in queryset:
            if send_whatsapp_notification(inquiry):
                success_count += 1
        
        self.message_user(
            request, 
            f"تم إرسال {success_count} من {queryset.count()} رسالة واتساب"
        )
    resend_whatsapp.short_description = "إعادة إرسال واتساب"


@admin.register(InquiryNote)
class InquiryNoteAdmin(admin.ModelAdmin):
    list_display = ['inquiry', 'note_preview', 'created_by', 'created_at']
    list_filter = ['created_at']
    search_fields = ['inquiry__name', 'note', 'created_by']
    readonly_fields = ['created_at']
    
    def note_preview(self, obj):
        """عرض أول 50 حرف من الملاحظة"""
        return obj.note[:50] + '...' if len(obj.note) > 50 else obj.note
    note_preview.short_description = 'الملاحظة'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('inquiry')


@admin.register(RecentWork)
class RecentWorkAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'service', 'rating_display', 
        'total_reviews', 'is_featured', 'is_active', 
        'order', 'created_at'
    ]
    list_filter = ['is_featured', 'is_active', 'service', 'created_at']
    search_fields = ['title', 'description']
    list_editable = ['order', 'is_featured', 'is_active']
    readonly_fields = ['created_at', 'updated_at', 'rating_display', 'image_preview']
    inlines = [ReviewInline]
    
    fieldsets = (
        ('Project Info', {
            'fields': ('title', 'description', 'service')
        }),
        ('Image', {
            'fields': ('image', 'image_preview')
        }),
        ('Display Settings', {
            'fields': ('is_featured', 'is_active', 'order')
        }),
        ('Statistics', {
            'fields': ('rating_display', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('service')
    
    def rating_display(self, obj):
        """Display average rating with stars"""
        avg_rating = obj.get_average_rating()
        total_reviews = obj.get_total_reviews()
        if avg_rating:
            stars = "⭐" * int(round(avg_rating))
            rating_text = f"{avg_rating:.1f}"
            return format_html(
                '{} ({}/5 - {} reviews)',
                stars, rating_text, total_reviews
            )
        return format_html('<span style="color: gray;">No reviews yet</span>')
    rating_display.short_description = 'Rating'
    
    def total_reviews(self, obj):
        """Display total reviews count"""
        return obj.get_total_reviews()
    total_reviews.short_description = 'Reviews'
    
    def image_preview(self, obj):
        """Display image preview"""
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 300px;" />',
                obj.image.url
            )
        return "No image"
    image_preview.short_description = 'Image Preview'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        'customer_name', 'recent_work', 'stars_display',
        'is_approved', 'created_at'
    ]
    list_filter = ['is_approved', 'rating', 'created_at']
    search_fields = ['customer_name', 'customer_email', 'review_text', 'recent_work__title']
    list_editable = ['is_approved']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Customer Info', {
            'fields': ('customer_name', 'customer_email')
        }),
        ('Review Details', {
            'fields': ('recent_work', 'rating', 'review_text')
        }),
        ('Moderation', {
            'fields': ('is_approved',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('recent_work')
    
    def stars_display(self, obj):
        """Display rating as stars"""
        return obj.get_stars_display()
    stars_display.short_description = 'Rating'
    
    actions = ['approve_reviews', 'unapprove_reviews']
    
    def approve_reviews(self, request, queryset):
        """Approve selected reviews"""
        count = queryset.update(is_approved=True)
        self.message_user(request, f"{count} reviews approved")
    approve_reviews.short_description = "Approve selected reviews"
    
    def unapprove_reviews(self, request, queryset):
        """Unapprove selected reviews"""
        count = queryset.update(is_approved=False)
        self.message_user(request, f"{count} reviews unapproved")
    unapprove_reviews.short_description = "Unapprove selected reviews"
