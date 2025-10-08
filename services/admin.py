# services/admin.py
from django.contrib import admin
from .models import ServiceCategory, Service, ServiceImage


class ServiceImageInline(admin.TabularInline):
    model = ServiceImage
    extra = 1
    fields = ['image', 'title', 'caption', 'is_before_after', 'order']


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_en', 'order', 'is_active', 'created_at']
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
        ('إعدادات العرض / Display Settings', {
            'fields': ('order', 'is_active')
        }),
    )


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'starting_price', 'order', 'is_featured', 'is_active', 'created_at']
    list_filter = ['is_active', 'is_featured', 'category', 'created_at']
    search_fields = ['title', 'title_en', 'description', 'short_description']
    prepopulated_fields = {'slug': ('title_en',)}
    list_editable = ['order', 'is_featured', 'is_active']
    inlines = [ServiceImageInline]
    
    fieldsets = (
        ('معلومات أساسية / Basic Info', {
            'fields': ('title', 'title_en', 'slug', 'category', 'icon')
        }),
        ('الوصف / Description', {
            'fields': ('short_description', 'description', 'features')
        }),
        ('الصورة / Image', {
            'fields': ('image',)
        }),
        ('السعر / Pricing', {
            'fields': ('starting_price',),
            'classes': ('collapse',)
        }),
        ('إعدادات العرض / Display Settings', {
            'fields': ('order', 'is_featured', 'is_active')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category')


@admin.register(ServiceImage)
class ServiceImageAdmin(admin.ModelAdmin):
    list_display = ['service', 'title', 'is_before_after', 'order', 'created_at']
    list_filter = ['is_before_after', 'created_at']
    search_fields = ['service__title', 'title', 'caption']
    list_editable = ['order']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('service')
