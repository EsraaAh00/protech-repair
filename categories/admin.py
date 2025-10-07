from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from .models import Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [
        'name_with_icon', 'parent_category', 'products_count', 
        'is_active_display', 'created_at_display', 'actions_display'
    ]
    list_filter = ['created_at', 'parent']
    search_fields = ['name', 'slug']
    list_per_page = 20
    date_hierarchy = 'created_at'
    ordering = ['name']
    
    fieldsets = (
        ('معلومات الفئة', {
            'fields': ('name', 'slug', 'parent'),
            'classes': ('wide',)
        }),
        ('التواريخ', {
            'fields': ('created_at',),
            'classes': ('collapse',),
            'description': 'تاريخ إنشاء الفئة'
        })
    )
    
    readonly_fields = ('created_at',)
    
    def name_with_icon(self, obj):
        # أيقونات مختلفة للفئات
        icons = {
            'السيارات': '🚗',
            'العقارات': '🏠',
            'الفنادق': '🏨',
            'الإلكترونيات': '📱',
            'الملابس': '👔',
            'الكتب': '📚'
        }
        icon = icons.get(obj.name, '📦')
        return format_html(
            '<span style="font-size: 20px; margin-left: 10px;">{}</span>'
            '<strong style="font-size: 16px;">{}</strong>',
            icon, obj.name
        )
    name_with_icon.short_description = "اسم الفئة"

    def parent_category(self, obj):
        if obj.parent:
            return format_html('<span style="color: #666;">{}</span>', obj.parent.name)
        return format_html('<span style="color: #ccc; font-style: italic;">فئة رئيسية</span>')
    parent_category.short_description = "الفئة الأب"

    def products_count(self, obj):
        count = obj.products.count()
        color = '#28a745' if count > 0 else '#6c757d'
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; border-radius: 20px; font-weight: bold; font-size: 14px;">'
            '{} منتج'
            '</span>',
            color, count
        )
    products_count.short_description = "عدد المنتجات"

    def is_active_display(self, obj):
        # تحديد إذا كانت الفئة نشطة بناء على وجود منتجات
        is_active = obj.products.filter(status='active').exists()
        color = '#28a745' if is_active else '#dc3545'
        status = 'نشطة' if is_active else 'غير نشطة'
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px; font-weight: bold;">'
            '{}'
            '</span>',
            color, status
        )
    is_active_display.short_description = "الحالة"

    def created_at_display(self, obj):
        return format_html(
            '<div>'
            '<strong>{}</strong><br>'
            '<small style="color: #666;">{}</small>'
            '</div>',
            obj.created_at.strftime('%Y/%m/%d'),
            obj.created_at.strftime('%H:%M')
        )
    created_at_display.short_description = "تاريخ الإنشاء"

    def actions_display(self, obj):
        return format_html(
            '<div style="display: flex; gap: 5px;">'
            '<a href="/categories/{}/products/" style="background: #007bff; color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none; font-size: 12px;">المنتجات</a>'
            '</div>',
            obj.id
        )
    actions_display.short_description = "إجراءات"

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            products_count=Count('products')
        )

# Customize the admin interface
admin.site.site_header = "إدارة دلال السعودية"
admin.site.site_title = "دلال السعودية - الإدارة"
admin.site.index_title = "مرحباً في لوحة التحكم"
