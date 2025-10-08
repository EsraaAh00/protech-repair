from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Sum
from django.utils.safestring import mark_safe
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'product_info', 'buyer_info', 'seller_info', 
        'total_amount_formatted', 'status_badge', 'order_date'
    ]
    list_filter = [
        'status', 'order_date', 'product__category'
    ]
    search_fields = [
        'buyer__username', 'buyer__first_name', 'buyer__last_name',
        'seller__username', 'seller__first_name', 'seller__last_name',
        'product__title', 'notes'
    ]
    readonly_fields = ['order_date', 'order_summary']
    ordering = ['-order_date']
    date_hierarchy = 'order_date'
    list_per_page = 25
    
    fieldsets = (
        ('معلومات الطلب', {
            'fields': ('product', 'buyer', 'seller', 'order_date')
        }),
        ('التفاصيل المالية', {
            'fields': ('total_amount', 'status')
        }),
        ('ملاحظات إضافية', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('ملخص الطلب', {
            'fields': ('order_summary',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_confirmed', 'mark_as_completed', 'mark_as_cancelled']
    
    def product_info(self, obj):
        """معلومات المنتج"""
        if obj.product:
            return format_html(
                '<a href="{}" target="_blank"><strong>{}</strong></a><br>'
                '<small>الفئة: {} | السعر الأصلي: {} ر.س</small>',
                reverse('admin:products_product_change', args=[obj.product.pk]),
                obj.product.title[:40] + '...' if len(obj.product.title) > 40 else obj.product.title,
                obj.product.category.name,
                obj.product.price
            )
        return '-'
    product_info.short_description = 'المنتج'
    
    def buyer_info(self, obj):
        """معلومات المشتري"""
        if obj.buyer:
            name = obj.buyer.get_full_name() or obj.buyer.username
            email = obj.buyer.email or 'لا يوجد إيميل'
            return format_html(
                '<strong>{}</strong><br>'
                '<small>المستخدم: {} | الإيميل: {}</small>',
                name, obj.buyer.username, email
            )
        return '-'
    buyer_info.short_description = 'المشتري'
    
    def seller_info(self, obj):
        """معلومات البائع"""
        if obj.seller:
            name = obj.seller.get_full_name() or obj.seller.username
            email = obj.seller.email or 'لا يوجد إيميل'
            return format_html(
                '<strong>{}</strong><br>'
                '<small>المستخدم: {} | الإيميل: {}</small>',
                name, obj.seller.username, email
            )
        elif obj.product and obj.product.seller:
            # استخدام بائع المنتج إذا لم يكن البائع محدد في الطلب
            seller = obj.product.seller
            name = seller.get_full_name() or seller.username
            return format_html(
                '<strong>{}</strong> <small>(من المنتج)</small><br>'
                '<small>المستخدم: {}</small>',
                name, seller.username
            )
        return '-'
    seller_info.short_description = 'البائع'
    
    def total_amount_formatted(self, obj):
        """المبلغ الإجمالي مع تنسيق"""
        return format_html(
            '<strong style="color: #28a745; font-size: 14px;">{} ر.س</strong>',
            f"{obj.total_amount:,.2f}"
        )
    total_amount_formatted.short_description = 'المبلغ الإجمالي'
    
    def status_badge(self, obj):
        """حالة الطلب مع ألوان"""
        status_colors = {
            'pending': ('#ffc107', '⏳ في الانتظار'),
            'confirmed': ('#17a2b8', '✅ مؤكد'),
            'completed': ('#28a745', '🎉 مكتمل'),
            'cancelled': ('#dc3545', '❌ ملغي'),
        }
        
        color, text = status_colors.get(obj.status, ('#6c757d', obj.get_status_display()))
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; '
            'border-radius: 12px; font-size: 12px; font-weight: bold;">{}</span>',
            color, text
        )
    status_badge.short_description = 'الحالة'
    
    def order_summary(self, obj):
        """ملخص شامل للطلب"""
        if not obj.pk:
            return 'احفظ الطلب أولاً لعرض الملخص'
        
        # حساب إحصائيات البائع والمشتري
        buyer_orders_count = Order.objects.filter(buyer=obj.buyer).count()
        seller_orders_count = Order.objects.filter(seller=obj.seller).count() if obj.seller else 0
        
        html_content = f'''
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <h4 style="color: #495057; margin-bottom: 15px;">📊 ملخص الطلب</h4>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div>
                    <h5 style="color: #6c757d;">معلومات المشتري:</h5>
                    <ul style="margin: 5px 0; padding-left: 20px;">
                        <li>إجمالي طلبات المشتري: <strong>{buyer_orders_count}</strong></li>
                        <li>تاريخ التسجيل: <strong>{obj.buyer.date_joined.strftime("%Y-%m-%d")}</strong></li>
                    </ul>
                </div>
                
                <div>
                    <h5 style="color: #6c757d;">معلومات البائع:</h5>
                    <ul style="margin: 5px 0; padding-left: 20px;">
                        <li>إجمالي طلبات البائع: <strong>{seller_orders_count}</strong></li>
                        <li>إجمالي المنتجات: <strong>{obj.product.seller.products.count() if obj.product else 0}</strong></li>
                        <li>تقييم البائع: <strong>⭐ غير متوفر</strong></li>
                    </ul>
                </div>
            </div>
            
            <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #dee2e6;">
                <h5 style="color: #6c757d;">تفاصيل المنتج:</h5>
                <ul style="margin: 5px 0; padding-left: 20px;">
                    <li>السعر الأصلي: <strong>{obj.product.price} ر.س</strong></li>
                    <li>المبلغ المدفوع: <strong>{obj.total_amount} ر.س</strong></li>
                    <li>الفرق: <strong>{float(obj.total_amount) - float(obj.product.price)} ر.س</strong></li>
                    <li>عدد المشاهدات: <strong>{obj.product.views_count}</strong></li>
                </ul>
            </div>
            
            {f'<div style="margin-top: 15px;"><h5 style="color: #6c757d;">الملاحظات:</h5><p style="background: white; padding: 10px; border-radius: 4px;">{obj.notes}</p></div>' if obj.notes else ''}
        </div>
        '''
        
        return mark_safe(html_content)
    order_summary.short_description = 'ملخص الطلب'
    
    # Actions
    def mark_as_confirmed(self, request, queryset):
        """تأكيد الطلبات"""
        updated = queryset.update(status='confirmed')
        self.message_user(request, f'تم تأكيد {updated} طلب.')
    mark_as_confirmed.short_description = 'تأكيد الطلبات المحددة'
    
    def mark_as_completed(self, request, queryset):
        """إكمال الطلبات"""
        updated = queryset.update(status='completed')
        # يمكن إضافة منطق إضافي هنا مثل تحديث حالة المنتج
        for order in queryset:
            if order.product and order.status == 'completed':
                order.product.is_sold = True
                order.product.status = 'sold'
                order.product.save()
        self.message_user(request, f'تم إكمال {updated} طلب.')
    mark_as_completed.short_description = 'إكمال الطلبات المحددة'
    
    def mark_as_cancelled(self, request, queryset):
        """إلغاء الطلبات"""
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'تم إلغاء {updated} طلب.')
    mark_as_cancelled.short_description = 'إلغاء الطلبات المحددة'
    
    # إضافة إحصائيات في أعلى الصفحة
    def changelist_view(self, request, extra_context=None):
        # إحصائيات سريعة
        total_orders = Order.objects.count()
        pending_orders = Order.objects.filter(status='pending').count()
        completed_orders = Order.objects.filter(status='completed').count()
        total_revenue = Order.objects.filter(status='completed').aggregate(
            total=Sum('total_amount')
        )['total'] or 0
        
        extra_context = extra_context or {}
        extra_context['total_orders'] = total_orders
        extra_context['pending_orders'] = pending_orders
        extra_context['completed_orders'] = completed_orders
        extra_context['total_revenue'] = total_revenue
        
        return super().changelist_view(request, extra_context=extra_context)
