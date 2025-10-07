from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Avg, Count
from django.utils.safestring import mark_safe
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'reviewer_info', 'target_info', 'rating_stars', 
        'comment_preview', 'timestamp'
    ]
    list_filter = [
        'rating', 'timestamp', 'product__category',
        'reviewer__is_seller', 'seller__is_seller'
    ]
    search_fields = [
        'reviewer__username', 'reviewer__first_name', 'reviewer__last_name',
        'seller__username', 'seller__first_name', 'seller__last_name',
        'product__title', 'comment'
    ]
    readonly_fields = ['timestamp', 'review_analysis']
    ordering = ['-timestamp']
    date_hierarchy = 'timestamp'
    list_per_page = 25
    
    fieldsets = (
        ('معلومات التقييم', {
            'fields': ('reviewer', 'rating', 'comment', 'timestamp')
        }),
        ('الهدف المقيم', {
            'fields': ('product', 'seller'),
            'description': 'يمكن أن يكون التقييم للمنتج أو للبائع أو لكليهما'
        }),
        ('تحليل التقييم', {
            'fields': ('review_analysis',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_reviews', 'hide_reviews']
    
    def reviewer_info(self, obj):
        """معلومات المراجع"""
        if obj.reviewer:
            name = obj.reviewer.get_full_name() or obj.reviewer.username
            badge = '🏪' if obj.reviewer.is_seller else '👤'
            reviews_count = Review.objects.filter(reviewer=obj.reviewer).count()
            return format_html(
                '<strong>{}</strong> {}<br>'
                '<small>المستخدم: {} | إجمالي التقييمات: {}</small>',
                name, badge, obj.reviewer.username, reviews_count
            )
        return '-'
    reviewer_info.short_description = 'المراجع'
    
    def target_info(self, obj):
        """معلومات الهدف المقيم"""
        if obj.product and obj.seller:
            # تقييم للمنتج والبائع معاً
            return format_html(
                '📦 <a href="{}" target="_blank">{}</a><br>'
                '👤 <a href="{}" target="_blank">{}</a>',
                reverse('admin:products_product_change', args=[obj.product.pk]),
                obj.product.title[:30] + '...' if len(obj.product.title) > 30 else obj.product.title,
                reverse('admin:users_user_change', args=[obj.seller.pk]),
                obj.seller.get_full_name() or obj.seller.username
            )
        elif obj.product:
            # تقييم للمنتج فقط
            return format_html(
                '📦 <a href="{}" target="_blank">{}</a><br>'
                '<small>السعر: {} ر.س | البائع: {}</small>',
                reverse('admin:products_product_change', args=[obj.product.pk]),
                obj.product.title[:30] + '...' if len(obj.product.title) > 30 else obj.product.title,
                obj.product.price,
                obj.product.seller.get_full_name() or obj.product.seller.username
            )
        elif obj.seller:
            # تقييم للبائع فقط
            seller_products_count = obj.seller.products.count()
            return format_html(
                '👤 <a href="{}" target="_blank">{}</a><br>'
                '<small>عدد المنتجات: {} | نوع الحساب: {}</small>',
                reverse('admin:users_user_change', args=[obj.seller.pk]),
                obj.seller.get_full_name() or obj.seller.username,
                seller_products_count,
                'بائع' if obj.seller.is_seller else 'مستخدم عادي'
            )
        return 'غير محدد'
    target_info.short_description = 'الهدف المقيم'
    
    def rating_stars(self, obj):
        """عرض التقييم بالنجوم"""
        stars = '⭐' * obj.rating + '☆' * (5 - obj.rating)
        color = {
            5: '#28a745',  # أخضر
            4: '#17a2b8',  # أزرق
            3: '#ffc107',  # أصفر
            2: '#fd7e14',  # برتقالي
            1: '#dc3545'   # أحمر
        }.get(obj.rating, '#6c757d')
        
        return format_html(
            '<span style="color: {}; font-size: 16px;">{}</span><br>'
            '<small>({}/5)</small>',
            color, stars, obj.rating
        )
    rating_stars.short_description = 'التقييم'
    
    def comment_preview(self, obj):
        """معاينة التعليق"""
        if len(obj.comment) > 60:
            return obj.comment[:60] + '...'
        return obj.comment
    comment_preview.short_description = 'التعليق'
    
    def review_analysis(self, obj):
        """تحليل شامل للتقييم"""
        if not obj.pk:
            return 'احفظ التقييم أولاً لعرض التحليل'
        
        # إحصائيات المراجع
        reviewer_stats = Review.objects.filter(reviewer=obj.reviewer).aggregate(
            total_reviews=Count('id'),
            avg_rating=Avg('rating')
        )
        
        html_content = f'''
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <h4 style="color: #495057; margin-bottom: 15px;">📊 تحليل التقييم</h4>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div>
                    <h5 style="color: #6c757d;">إحصائيات المراجع:</h5>
                    <ul style="margin: 5px 0; padding-left: 20px;">
                        <li>إجمالي التقييمات: <strong>{reviewer_stats['total_reviews']}</strong></li>
                        <li>متوسط التقييمات: <strong>{reviewer_stats['avg_rating']:.1f if reviewer_stats['avg_rating'] else 0}/5</strong></li>
                        <li>تاريخ التسجيل: <strong>{obj.reviewer.date_joined.strftime("%Y-%m-%d")}</strong></li>
                        <li>نوع الحساب: <strong>{'بائع' if obj.reviewer.is_seller else 'مشتري'}</strong></li>
                    </ul>
                </div>
                
                <div>
                    <h5 style="color: #6c757d;">تفاصيل التقييم:</h5>
                    <div style="background: white; padding: 15px; border-radius: 4px;">
                        <p><strong>التقييم:</strong> {obj.rating}/5 ({'ممتاز' if obj.rating == 5 else 'جيد جداً' if obj.rating == 4 else 'جيد' if obj.rating == 3 else 'مقبول' if obj.rating == 2 else 'ضعيف'})</p>
                        <p><strong>طول التعليق:</strong> {len(obj.comment)} حرف</p>
                        <div style="margin-top: 10px;">
                            <strong>التعليق الكامل:</strong>
                            <div style="background: #f8f9fa; padding: 10px; border-radius: 4px; margin-top: 5px; font-style: italic;">
                                "{obj.comment}"
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        '''
        
        return mark_safe(html_content)
    review_analysis.short_description = 'تحليل التقييم'
    
    # Actions
    def approve_reviews(self, request, queryset):
        """الموافقة على التقييمات (يمكن إضافة منطق الموافقة لاحقاً)"""
        count = queryset.count()
        self.message_user(request, f'تمت الموافقة على {count} تقييم.')
    approve_reviews.short_description = 'الموافقة على التقييمات المحددة'
    
    def hide_reviews(self, request, queryset):
        """إخفاء التقييمات (يمكن إضافة حقل is_hidden لاحقاً)"""
        count = queryset.count()
        self.message_user(request, f'تم إخفاء {count} تقييم.')
    hide_reviews.short_description = 'إخفاء التقييمات المحددة'
    
    # إضافة إحصائيات في أعلى الصفحة
    def changelist_view(self, request, extra_context=None):
        # إحصائيات سريعة
        total_reviews = Review.objects.count()
        avg_rating = Review.objects.aggregate(avg=Avg('rating'))['avg'] or 0
        five_star_reviews = Review.objects.filter(rating=5).count()
        one_star_reviews = Review.objects.filter(rating=1).count()
        
        extra_context = extra_context or {}
        extra_context['total_reviews'] = total_reviews
        extra_context['avg_rating'] = round(avg_rating, 1)
        extra_context['five_star_reviews'] = five_star_reviews
        extra_context['one_star_reviews'] = one_star_reviews
        
        return super().changelist_view(request, extra_context=extra_context)
