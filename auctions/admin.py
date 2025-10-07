from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Max, Sum
from django.utils.safestring import mark_safe
from django.utils import timezone
from .models import Auction, Bid

class BidInline(admin.TabularInline):
    model = Bid
    extra = 0
    readonly_fields = ['bid_time', 'is_winning']
    fields = ['bidder', 'amount', 'bid_time', 'is_winning']
    ordering = ['-amount', '-bid_time']
    
    def has_add_permission(self, request, obj=None):
        return False  # منع إضافة مزايدات من الإدارة

@admin.register(Auction)
class AuctionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'product_info', 'time_info', 'bid_info', 
        'status_badge', 'auction_progress'
    ]
    list_filter = [
        'status', 'start_time', 'end_time', 'product__category',
        'product__seller__is_seller'
    ]
    search_fields = [
        'product__title', 'product__seller__username',
        'highest_bidder__username', 'highest_bidder__first_name'
    ]
    readonly_fields = ['created_at', 'auction_summary', 'current_bid']
    ordering = ['-created_at']
    date_hierarchy = 'start_time'
    list_per_page = 20
    inlines = [BidInline]
    
    fieldsets = (
        ('معلومات المزاد', {
            'fields': ('product', 'status', 'created_at')
        }),
        ('توقيتات المزاد', {
            'fields': ('start_time', 'end_time')
        }),
        ('معلومات المزايدة', {
            'fields': ('starting_bid', 'current_bid', 'highest_bidder')
        }),
        ('ملخص المزاد', {
            'fields': ('auction_summary',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['close_auctions', 'cancel_auctions', 'activate_auctions']
    
    def product_info(self, obj):
        """معلومات المنتج"""
        if obj.product:
            return format_html(
                '<a href="{}" target="_blank"><strong>{}</strong></a><br>'
                '<small>البائع: {} | السعر الأصلي: {} ر.س</small>',
                reverse('admin:products_product_change', args=[obj.product.pk]),
                obj.product.title[:40] + '...' if len(obj.product.title) > 40 else obj.product.title,
                obj.product.seller.get_full_name() or obj.product.seller.username,
                obj.product.price
            )
        return '-'
    product_info.short_description = 'المنتج'
    
    def time_info(self, obj):
        """معلومات التوقيت"""
        now = timezone.now()
        
        if now < obj.start_time:
            status = '⏰ لم يبدأ بعد'
            time_left = obj.start_time - now
        elif now > obj.end_time:
            status = '⏰ انتهى'
            time_left = now - obj.end_time
        else:
            status = '🔴 جاري الآن'
            time_left = obj.end_time - now
        
        return format_html(
            '<strong>{}</strong><br>'
            '<small>البداية: {}</small><br>'
            '<small>النهاية: {}</small><br>'
            '<small>المدة المتبقية: {} يوم</small>',
            status,
            obj.start_time.strftime('%Y-%m-%d %H:%M'),
            obj.end_time.strftime('%Y-%m-%d %H:%M'),
            time_left.days if time_left.days > 0 else 0
        )
    time_info.short_description = 'التوقيت'
    
    def bid_info(self, obj):
        """معلومات المزايدة"""
        bids_count = obj.bids.count()
        current_bid = obj.current_bid or obj.starting_bid
        
        if obj.highest_bidder:
            winner_info = format_html(
                '<br><small>أعلى مزايد: {}</small>',
                obj.highest_bidder.get_full_name() or obj.highest_bidder.username
            )
        else:
            winner_info = '<br><small>لا توجد مزايدات</small>'
        
        return format_html(
            '<strong>{} ر.س</strong> (بداية: {} ر.س)<br>'
            '<small>عدد المزايدات: {}</small>{}',
            current_bid,
            obj.starting_bid,
            bids_count,
            winner_info
        )
    bid_info.short_description = 'المزايدة'
    
    def status_badge(self, obj):
        """حالة المزاد مع ألوان"""
        status_colors = {
            'active': ('#28a745', '🟢 نشط'),
            'closed': ('#6c757d', '⚫ مغلق'),
            'cancelled': ('#dc3545', '🔴 ملغي'),
        }
        
        color, text = status_colors.get(obj.status, ('#6c757d', obj.get_status_display()))
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 4px 8px; '
            'border-radius: 12px; font-size: 12px; font-weight: bold;">{}</span>',
            color, text
        )
    status_badge.short_description = 'الحالة'
    
    def auction_progress(self, obj):
        """تقدم المزاد"""
        now = timezone.now()
        total_duration = (obj.end_time - obj.start_time).total_seconds()
        
        if now < obj.start_time:
            progress = 0
            status = 'لم يبدأ'
        elif now > obj.end_time:
            progress = 100
            status = 'انتهى'
        else:
            elapsed = (now - obj.start_time).total_seconds()
            progress = min(100, (elapsed / total_duration) * 100)
            status = f'{progress:.0f}% مكتمل'
        
        return format_html(
            '<div style="width: 100px; background: #e9ecef; border-radius: 10px; height: 8px; position: relative;">'
            '<div style="width: {}%; background: #007bff; height: 100%; border-radius: 10px;"></div>'
            '</div><small>{}</small>',
            progress, status
        )
    auction_progress.short_description = 'التقدم'
    
    def auction_summary(self, obj):
        """ملخص شامل للمزاد"""
        if not obj.pk:
            return 'احفظ المزاد أولاً لعرض الملخص'
        
        # إحصائيات المزايدات
        bids_stats = obj.bids.aggregate(
            total_bids=Count('id'),
            max_bid=Max('amount'),
            unique_bidders=Count('bidder', distinct=True)
        )
        
        # أعلى 5 مزايدات
        top_bids = obj.bids.select_related('bidder').order_by('-amount')[:5]
        
        html_content = f'''
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <h4 style="color: #495057; margin-bottom: 15px;">🏆 ملخص المزاد</h4>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div>
                    <h5 style="color: #6c757d;">إحصائيات المزايدة:</h5>
                    <ul style="margin: 5px 0; padding-left: 20px;">
                        <li>إجمالي المزايدات: <strong>{bids_stats['total_bids']}</strong></li>
                        <li>عدد المزايدين: <strong>{bids_stats['unique_bidders']}</strong></li>
                        <li>أعلى مزايدة: <strong>{bids_stats['max_bid'] or 'لا توجد'} ر.س</strong></li>
                        <li>السعر الابتدائي: <strong>{obj.starting_bid} ر.س</strong></li>
                    </ul>
                </div>
                
                <div>
                    <h5 style="color: #6c757d;">معلومات التوقيت:</h5>
                    <ul style="margin: 5px 0; padding-left: 20px;">
                        <li>تاريخ الإنشاء: <strong>{obj.created_at.strftime("%Y-%m-%d %H:%M")}</strong></li>
                        <li>بداية المزاد: <strong>{obj.start_time.strftime("%Y-%m-%d %H:%M")}</strong></li>
                        <li>نهاية المزاد: <strong>{obj.end_time.strftime("%Y-%m-%d %H:%M")}</strong></li>
                        <li>المدة الإجمالية: <strong>{(obj.end_time - obj.start_time).days} يوم</strong></li>
                    </ul>
                </div>
            </div>
        '''
        
        if top_bids:
            html_content += '''
            <div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid #dee2e6;">
                <h5 style="color: #6c757d;">أعلى المزايدات:</h5>
                <div style="background: white; padding: 10px; border-radius: 4px;">
            '''
            
            for i, bid in enumerate(top_bids, 1):
                badge_color = '#ffd700' if i == 1 else '#c0c0c0' if i == 2 else '#cd7f32' if i == 3 else '#6c757d'
                html_content += f'''
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 5px 0; border-bottom: 1px solid #f0f0f0;">
                        <span style="background: {badge_color}; color: white; width: 20px; height: 20px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: 12px; font-weight: bold;">{i}</span>
                        <span><strong>{bid.bidder.get_full_name() or bid.bidder.username}</strong></span>
                        <span style="color: #28a745; font-weight: bold;">{bid.amount} ر.س</span>
                        <small style="color: #6c757d;">{bid.bid_time.strftime("%m-%d %H:%M")}</small>
                    </div>
                '''
            
            html_content += '</div></div>'
        
        html_content += '</div>'
        
        return mark_safe(html_content)
    auction_summary.short_description = 'ملخص المزاد'
    
    # Actions
    def close_auctions(self, request, queryset):
        """إغلاق المزادات"""
        updated = queryset.update(status='closed')
        self.message_user(request, f'تم إغلاق {updated} مزاد.')
    close_auctions.short_description = 'إغلاق المزادات المحددة'
    
    def cancel_auctions(self, request, queryset):
        """إلغاء المزادات"""
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'تم إلغاء {updated} مزاد.')
    cancel_auctions.short_description = 'إلغاء المزادات المحددة'
    
    def activate_auctions(self, request, queryset):
        """تفعيل المزادات"""
        updated = queryset.update(status='active')
        self.message_user(request, f'تم تفعيل {updated} مزاد.')
    activate_auctions.short_description = 'تفعيل المزادات المحددة'

@admin.register(Bid)
class BidAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'auction_info', 'bidder_info', 'amount_formatted', 
        'bid_time', 'is_winning_badge'
    ]
    list_filter = [
        'bid_time', 'is_winning', 'auction__status',
        'bidder__is_seller'
    ]
    search_fields = [
        'bidder__username', 'bidder__first_name', 'bidder__last_name',
        'auction__product__title'
    ]
    readonly_fields = ['bid_time']
    ordering = ['-bid_time']
    date_hierarchy = 'bid_time'
    list_per_page = 30
    
    def auction_info(self, obj):
        """معلومات المزاد"""
        return format_html(
            '<a href="{}" target="_blank"><strong>مزاد #{}</strong></a><br>'
            '<small>{}</small>',
            reverse('admin:auctions_auction_change', args=[obj.auction.pk]),
            obj.auction.pk,
            obj.auction.product.title[:30] + '...' if len(obj.auction.product.title) > 30 else obj.auction.product.title
        )
    auction_info.short_description = 'المزاد'
    
    def bidder_info(self, obj):
        """معلومات المزايد"""
        name = obj.bidder.get_full_name() or obj.bidder.username
        badge = '🏪' if obj.bidder.is_seller else '👤'
        bids_count = Bid.objects.filter(bidder=obj.bidder).count()
        return format_html(
            '<strong>{}</strong> {}<br>'
            '<small>إجمالي المزايدات: {}</small>',
            name, badge, bids_count
        )
    bidder_info.short_description = 'المزايد'
    
    def amount_formatted(self, obj):
        """المبلغ مع تنسيق"""
        return format_html(
            '<strong style="color: #28a745; font-size: 14px;">{} ر.س</strong>',
            f"{obj.amount:,.2f}"
        )
    amount_formatted.short_description = 'المبلغ'
    
    def is_winning_badge(self, obj):
        """حالة الفوز"""
        if obj.is_winning:
            return format_html('<span style="color: #28a745;">🏆 فائز</span>')
        else:
            return format_html('<span style="color: #6c757d;">-</span>')
    is_winning_badge.short_description = 'حالة الفوز'
