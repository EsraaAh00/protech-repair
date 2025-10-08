# products/admin.py
from django.contrib import admin
from .models import (
    ProductCategory, Product, ProductImage,
    OpenerSpecifications, DoorSpecifications
)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'title', 'is_main', 'order']


class OpenerSpecificationsInline(admin.StackedInline):
    model = OpenerSpecifications
    can_delete = False
    verbose_name = "مواصفات الفتاحة"
    verbose_name_plural = "مواصفات الفتاحة"
    
    fieldsets = (
        ('المحرك / Drive', {
            'fields': ('drive_type', 'horsepower', 'lifting_capacity', 'speed')
        }),
        ('الميزات الذكية / Smart Features', {
            'fields': ('has_wifi', 'has_battery_backup', 'has_camera', 'has_smart_features')
        }),
        ('مواصفات إضافية / Additional Specs', {
            'fields': ('noise_level', 'warranty_years')
        }),
    )


class DoorSpecificationsInline(admin.StackedInline):
    model = DoorSpecifications
    can_delete = False
    verbose_name = "مواصفات الباب"
    verbose_name_plural = "مواصفات الباب"
    
    fieldsets = (
        ('المادة والتصميم / Material & Design', {
            'fields': ('panel_style', 'material', 'texture_options')
        }),
        ('المقاسات / Dimensions', {
            'fields': ('width_options', 'height_options')
        }),
        ('العزل / Insulation', {
            'fields': ('insulation_type', 'r_value')
        }),
        ('الألوان والنوافذ / Colors & Windows', {
            'fields': ('color_options', 'has_windows', 'window_options')
        }),
        ('الضمان / Warranty', {
            'fields': ('warranty_years',)
        }),
    )


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_en', 'slug', 'order', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'name_en', 'description']
    prepopulated_fields = {'slug': ('name_en',)}
    list_editable = ['order', 'is_active']
    
    fieldsets = (
        ('معلومات أساسية / Basic Info', {
            'fields': ('name', 'name_en', 'slug', 'icon')
        }),
        ('الوصف / Description', {
            'fields': ('description',)
        }),
        ('الصورة / Image', {
            'fields': ('image',)
        }),
        ('إعدادات العرض / Display Settings', {
            'fields': ('order', 'is_active')
        }),
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'model_number', 'category', 'product_type', 
        'price', 'is_featured', 'is_best_seller', 'is_active', 
        'views_count', 'created_at'
    ]
    list_filter = [
        'is_active', 'is_featured', 'is_best_seller', 'is_new',
        'product_type', 'category', 'created_at'
    ]
    search_fields = ['name', 'name_en', 'model_number', 'brand', 'description']
    prepopulated_fields = {'slug': ('name_en',)}
    list_editable = ['is_featured', 'is_best_seller', 'is_active']
    inlines = [ProductImageInline]
    readonly_fields = ['views_count', 'created_at', 'updated_at']
    
    fieldsets = (
        ('معلومات أساسية / Basic Info', {
            'fields': (
                'name', 'name_en', 'slug', 'model_number', 
                'category', 'product_type', 'brand'
            )
        }),
        ('الوصف / Description', {
            'fields': ('short_description', 'description', 'features', 'specifications')
        }),
        ('الصورة / Image', {
            'fields': ('image',)
        }),
        ('السعر / Pricing', {
            'fields': ('price',)
        }),
        ('إعدادات العرض / Display Settings', {
            'fields': (
                'is_featured', 'is_best_seller', 'is_new',
                'order', 'is_active'
            )
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('إحصائيات / Statistics', {
            'fields': ('views_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category')
    
    def get_inlines(self, request, obj=None):
        """Add appropriate inline based on product type"""
        inlines = [ProductImageInline]
        if obj:
            if obj.product_type == 'opener':
                inlines.append(OpenerSpecificationsInline)
            elif obj.product_type == 'door':
                inlines.append(DoorSpecificationsInline)
        return inlines
    
    actions = ['mark_as_featured', 'mark_as_not_featured', 'mark_as_active', 'mark_as_inactive']
    
    def mark_as_featured(self, request, queryset):
        queryset.update(is_featured=True)
        self.message_user(request, f"{queryset.count()} منتج تم تمييزه")
    mark_as_featured.short_description = "تمييز المنتجات المحددة"
    
    def mark_as_not_featured(self, request, queryset):
        queryset.update(is_featured=False)
        self.message_user(request, f"{queryset.count()} منتج تم إلغاء تمييزه")
    mark_as_not_featured.short_description = "إلغاء تمييز المنتجات المحددة"
    
    def mark_as_active(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} منتج تم تفعيله")
    mark_as_active.short_description = "تفعيل المنتجات المحددة"
    
    def mark_as_inactive(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} منتج تم إيقافه")
    mark_as_inactive.short_description = "إيقاف المنتجات المحددة"


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'title', 'is_main', 'order', 'created_at']
    list_filter = ['is_main', 'created_at']
    search_fields = ['product__name', 'title']
    list_editable = ['is_main', 'order']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product')


@admin.register(OpenerSpecifications)
class OpenerSpecificationsAdmin(admin.ModelAdmin):
    list_display = [
        'product', 'drive_type', 'horsepower', 
        'has_wifi', 'has_battery_backup', 'has_camera'
    ]
    list_filter = [
        'drive_type', 'has_wifi', 'has_battery_backup', 
        'has_camera', 'has_smart_features'
    ]
    search_fields = ['product__name', 'product__model_number']
    
    fieldsets = (
        ('المحرك / Drive', {
            'fields': ('product', 'drive_type', 'horsepower', 'lifting_capacity', 'speed')
        }),
        ('الميزات الذكية / Smart Features', {
            'fields': ('has_wifi', 'has_battery_backup', 'has_camera', 'has_smart_features')
        }),
        ('مواصفات إضافية / Additional Specs', {
            'fields': ('noise_level', 'warranty_years')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product')


@admin.register(DoorSpecifications)
class DoorSpecificationsAdmin(admin.ModelAdmin):
    list_display = [
        'product', 'panel_style', 'material', 
        'insulation_type', 'has_windows'
    ]
    list_filter = [
        'panel_style', 'material', 'insulation_type', 'has_windows'
    ]
    search_fields = ['product__name', 'product__model_number']
    
    fieldsets = (
        ('المادة والتصميم / Material & Design', {
            'fields': ('product', 'panel_style', 'material', 'texture_options')
        }),
        ('المقاسات / Dimensions', {
            'fields': ('width_options', 'height_options')
        }),
        ('العزل / Insulation', {
            'fields': ('insulation_type', 'r_value')
        }),
        ('الألوان والنوافذ / Colors & Windows', {
            'fields': ('color_options', 'has_windows', 'window_options')
        }),
        ('الضمان / Warranty', {
            'fields': ('warranty_years',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product')
