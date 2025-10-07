from django.contrib import admin, messages
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db import models
from django.contrib.admin import SimpleListFilter
from .models import Product, ProductImage, Car, RealEstate, HotelBooking

# Custom filters
class StatusFilter(SimpleListFilter):
    title = 'حالة المنتج'
    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return [
            ('pending_approval', 'بانتظار الموافقة'),
            ('active', 'نشط'),
            ('sold', 'مباع'),
            ('hidden', 'مخفي'),
            ('cancelled', 'ملغي'),
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())
        return queryset

class CategoryFilter(SimpleListFilter):
    title = 'الفئة'
    parameter_name = 'category'

    def lookups(self, request, model_admin):
        from categories.models import Category
        return [(cat.id, cat.name) for cat in Category.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(category_id=self.value())
        return queryset

class PriceRangeFilter(SimpleListFilter):
    title = 'نطاق السعر'
    parameter_name = 'price_range'

    def lookups(self, request, model_admin):
        return [
            ('0-1000', 'أقل من 1,000 ر.س'),
            ('1000-5000', '1,000 - 5,000 ر.س'),
            ('5000-20000', '5,000 - 20,000 ر.س'),
            ('20000-50000', '20,000 - 50,000 ر.س'),
            ('50000+', 'أكثر من 50,000 ر.س'),
        ]

    def queryset(self, request, queryset):
        if self.value() == '0-1000':
            return queryset.filter(price__lt=1000)
        elif self.value() == '1000-5000':
            return queryset.filter(price__gte=1000, price__lt=5000)
        elif self.value() == '5000-20000':
            return queryset.filter(price__gte=5000, price__lt=20000)
        elif self.value() == '20000-50000':
            return queryset.filter(price__gte=20000, price__lt=50000)
        elif self.value() == '50000+':
            return queryset.filter(price__gte=50000)
        return queryset

# Inline for Product Images
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3
    fields = ('image', 'is_main', 'image_preview')
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 100px; height: 100px; object-fit: cover; border-radius: 8px;" />',
                obj.image.url
            )
        return "لا توجد صورة"
    image_preview.short_description = "معاينة"

# Inline for Car Details
class CarInline(admin.StackedInline):
    model = Car
    extra = 0
    fields = (
        ('make', 'model', 'year'),
        ('mileage', 'color'),
        ('transmission_type', 'fuel_type'),
        'is_new'
    )

# Inline for Real Estate Details
class RealEstateInline(admin.StackedInline):
    model = RealEstate
    extra = 0
    fields = (
        ('property_type', 'area_sqm'),
        ('num_bedrooms', 'num_bathrooms'),
        ('is_furnished', 'for_rent')
    )

# Inline for Hotel Details
class HotelBookingInline(admin.StackedInline):
    model = HotelBooking
    extra = 0
    fields = (
        'hotel_name',
        ('room_type', 'num_guests'),
        ('check_in_date', 'check_out_date')
    )

def mark_as_sold(modeladmin, request, queryset):
    """تحديد المنتجات كمباعة"""
    updated = queryset.update(status='sold')
    messages.success(request, f'تم تحديد {updated} منتج كمباع')
mark_as_sold.short_description = 'تحديد كمباع'

def mark_as_active(modeladmin, request, queryset):
    """تحديد المنتجات كنشطة"""
    updated = queryset.update(status='active')
    messages.success(request, f'تم تفعيل {updated} منتج')
mark_as_active.short_description = 'تفعيل المنتجات'

def mark_as_pending(modeladmin, request, queryset):
    """تحديد المنتجات كفي الانتظار"""
    updated = queryset.update(status='pending_approval')
    messages.success(request, f'تم تحديد {updated} منتج كفي الانتظار')
mark_as_pending.short_description = 'في الانتظار'

# Main Product Admin
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'product_preview', 'seller_info', 'price_display', 'status_display', 
        'category_display', 'views_stats', 'messages_count', 'created_display'
    ]
    list_filter = [
        'status', 'category', 'created_at', 'seller__is_seller',
        'is_approved', 'is_sold'
    ]
    search_fields = [
        'title', 'description', 'seller__username', 
        'seller__first_name', 'seller__last_name'
    ]
    readonly_fields = ['created_at', 'updated_at', 'views_count', 'product_stats']
    filter_horizontal = []
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    list_per_page = 25
    actions = [mark_as_sold, mark_as_active, mark_as_pending]
    
    fieldsets = (
        ('معلومات المنتج الأساسية', {
            'fields': ('title', 'description', 'seller', 'category', 'price'),
            'classes': ('wide',)
        }),
        ('الحالة والإعدادات', {
            'fields': ('status', 'is_approved', 'is_sold'),
            'classes': ('wide',)
        }),
        ('الموقع', {
            'fields': ('location_latitude', 'location_longitude'),
            'classes': ('collapse', 'wide')
        }),
        ('إحصائيات المنتج', {
            'fields': ('product_stats',),
            'classes': ('collapse', 'wide')
        }),
        ('معلومات النظام', {
            'fields': ('views_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def product_preview(self, obj):
        """معاينة المنتج مع صورة وتفاصيل"""
        # محاولة الحصول على أول صورة
        first_image = obj.images.first()
        image_html = ''
        if first_image and first_image.image:
            image_html = f'<img src="{first_image.image.url}" style="width: 70px; height: 70px; object-fit: cover; border-radius: 8px; margin-left: 10px; float: left;">'
        
        return format_html(
            '<div style="display: flex; align-items: center; min-height: 70px;">'
            '{}'
            '<div style="flex: 1;">'
            '<strong style="color: #495057; font-size: 14px;">{}</strong><br>'
            '<small style="color: #6c757d; font-size: 11px;">{}</small><br>'
            '<small style="color: #007bff; font-size: 10px;">ID: #{}</small>'
            '</div>'
            '</div>',
            image_html,
            obj.title[:40] + '...' if len(obj.title) > 40 else obj.title,
            obj.description[:60] + '...' if len(obj.description) > 60 else obj.description,
            obj.pk
        )
    product_preview.short_description = 'المنتج'
    
    def seller_info(self, obj):
        """معلومات البائع"""
        seller_name = obj.seller.get_full_name() or obj.seller.username
        
        # حساب عدد منتجات البائع
        seller_products_count = Product.objects.filter(seller=obj.seller).count()
        
        return format_html(
            '<div style="text-align: center;">'
            '<div style="margin-bottom: 5px;">'
            '<a href="{}" target="_blank" style="text-decoration: none; color: #007bff; font-weight: bold;">'
            '{}'
            '</a>'
            '</div>'
            '<small style="color: #6c757d; font-size: 10px;">{} منتج</small><br>'
            '<span style="background: {}; color: white; padding: 2px 6px; border-radius: 10px; font-size: 9px;">{}</span>'
            '</div>',
            reverse('admin:users_customuser_change', args=[obj.seller.pk]),
            seller_name,
            seller_products_count,
            '#28a745' if obj.seller.is_seller else '#6c757d',
            'بائع' if obj.seller.is_seller else 'مستخدم'
        )
    seller_info.short_description = 'البائع'
    
    def price_display(self, obj):
        """عرض السعر مع تنسيق"""
        return format_html(
            '<div style="text-align: center;">'
            '<div style="font-size: 18px; font-weight: bold; color: #28a745; margin-bottom: 3px;">{}</div>'
            '<div style="font-size: 10px; color: #6c757d;">ريال سعودي</div>'
            '</div>',
            f'{obj.price:,.0f}'
        )
    price_display.short_description = 'السعر'
    
    def status_display(self, obj):
        """عرض الحالة مع ألوان ورموز"""
        status_config = {
            'active': ('نشط', '#28a745', '🟢'),
            'pending_approval': ('في الانتظار', '#ffc107', '🟡'),
            'sold': ('مباع', '#dc3545', '🔴'),
            'inactive': ('غير نشط', '#6c757d', '⚫')
        }
        
        if obj.status in status_config:
            label, color, icon = status_config[obj.status]
            return format_html(
                '<div style="text-align: center;">'
                '<div style="font-size: 16px; margin-bottom: 3px;">{}</div>'
                '<span style="background: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 10px; font-weight: bold;">{}</span>'
                '</div>',
                icon, color, label
            )
        
        return obj.status
    status_display.short_description = 'الحالة'
    
    def category_display(self, obj):
        """عرض الفئة"""
        return format_html(
            '<div style="text-align: center;">'
            '<a href="{}" target="_blank" style="text-decoration: none; color: #007bff; font-weight: bold;">{}</a>'
            '</div>',
            reverse('admin:categories_category_change', args=[obj.category.pk]),
            obj.category.name
        )
    category_display.short_description = 'الفئة'
    
    def views_stats(self, obj):
        """إحصائيات المشاهدات"""
        return format_html(
            '<div style="text-align: center;">'
            '<div style="font-size: 16px; font-weight: bold; color: #007bff; margin-bottom: 3px;">{}</div>'
            '<div style="font-size: 10px; color: #6c757d;">مشاهدة</div>'
            '</div>',
            obj.views_count or 0
        )
    views_stats.short_description = 'المشاهدات'
    
    def messages_count(self, obj):
        """عدد الرسائل المتعلقة بالمنتج"""
        from messaging.models import Message
        messages_count = Message.objects.filter(product=obj).count()
        conversations_count = obj.conversations.count()
        
        return format_html(
            '<div style="text-align: center;">'
            '<div style="font-size: 14px; font-weight: bold; color: #6c757d; margin-bottom: 3px;">{}</div>'
            '<div style="font-size: 10px; color: #6c757d;">رسالة</div>'
            '<div style="font-size: 10px; color: #007bff; margin-top: 2px;">{} محادثة</div>'
            '</div>',
            messages_count,
            conversations_count
        )
    messages_count.short_description = 'الرسائل'
    
    def created_display(self, obj):
        """تاريخ الإنشاء مع تنسيق"""
        from django.utils import timezone
        time_diff = timezone.now() - obj.created_at
        
        if time_diff.days > 0:
            time_str = f'{time_diff.days} يوم'
        elif time_diff.seconds > 3600:
            time_str = f'{time_diff.seconds // 3600} ساعة'
        elif time_diff.seconds > 60:
            time_str = f'{time_diff.seconds // 60} دقيقة'
        else:
            time_str = 'الآن'
        
        return format_html(
            '<div style="text-align: center;">'
            '<div style="font-size: 12px; color: #6c757d; margin-bottom: 3px;">{}</div>'
            '<div style="font-size: 10px; color: #6c757d;">منذ {}</div>'
            '</div>',
            obj.created_at.strftime('%Y-%m-%d'),
            time_str
        )
    created_display.short_description = 'تاريخ الإنشاء'
    
    def product_stats(self, obj):
        """إحصائيات شاملة للمنتج"""
        if not obj.pk:
            return 'احفظ المنتج أولاً لعرض الإحصائيات'
        
        from messaging.models import Message, Conversation
        
        # إحصائيات الرسائل والمحادثات
        messages_count = Message.objects.filter(product=obj).count()
        conversations_count = obj.conversations.count()
        unread_messages = Message.objects.filter(product=obj, is_read=False).count()
        
        # إحصائيات أخرى
        images_count = obj.images.count()
        
        html_content = f'''
        <div style="background: #f8f9fa; padding: 20px; border-radius: 12px; margin: 15px 0;">
            <h3 style="color: #495057; margin-bottom: 20px; text-align: center;">📊 إحصائيات المنتج</h3>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px;">
                <div style="background: white; padding: 15px; border-radius: 8px; text-align: center; border-left: 4px solid #007bff;">
                    <h4 style="color: #007bff; margin: 0 0 10px 0; font-size: 14px;">المشاهدات</h4>
                    <div style="font-size: 20px; font-weight: bold; color: #495057;">{obj.views_count or 0}</div>
                </div>
                
                <div style="background: white; padding: 15px; border-radius: 8px; text-align: center; border-left: 4px solid #28a745;">
                    <h4 style="color: #28a745; margin: 0 0 10px 0; font-size: 14px;">المحادثات</h4>
                    <div style="font-size: 20px; font-weight: bold; color: #495057;">{conversations_count}</div>
                </div>
                
                <div style="background: white; padding: 15px; border-radius: 8px; text-align: center; border-left: 4px solid #ffc107;">
                    <h4 style="color: #ffc107; margin: 0 0 10px 0; font-size: 14px;">الرسائل</h4>
                    <div style="font-size: 20px; font-weight: bold; color: #495057;">{messages_count}</div>
                </div>
                
                <div style="background: white; padding: 15px; border-radius: 8px; text-align: center; border-left: 4px solid #dc3545;">
                    <h4 style="color: #dc3545; margin: 0 0 10px 0; font-size: 14px;">غير مقروءة</h4>
                    <div style="font-size: 20px; font-weight: bold; color: #495057;">{unread_messages}</div>
                </div>
                
                <div style="background: white; padding: 15px; border-radius: 8px; text-align: center; border-left: 4px solid #6c757d;">
                    <h4 style="color: #6c757d; margin: 0 0 10px 0; font-size: 14px;">الصور</h4>
                    <div style="font-size: 20px; font-weight: bold; color: #495057;">{images_count}</div>
                </div>
            </div>
            
            <div style="background: white; padding: 15px; border-radius: 8px; margin-top: 15px;">
                <h4 style="color: #6c757d; margin-bottom: 10px; font-size: 14px;">معلومات إضافية</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 12px;">
                    <div><strong>تاريخ الإنشاء:</strong> {obj.created_at.strftime("%Y-%m-%d %H:%M")}</div>
                    <div><strong>آخر تحديث:</strong> {obj.updated_at.strftime("%Y-%m-%d %H:%M")}</div>
                    <div><strong>معتمد:</strong> {'نعم' if obj.is_approved else 'لا'}</div>
                    <div><strong>مباع:</strong> {'نعم' if obj.is_sold else 'لا'}</div>
                </div>
            </div>
        </div>
        '''
        
        return mark_safe(html_content)
    product_stats.short_description = 'إحصائيات المنتج'

# Car Admin
@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ['product_title', 'make_model_year', 'mileage_display', 'fuel_transmission', 'color', 'price_display']
    list_filter = ['make', 'fuel_type', 'transmission_type', 'is_new', 'year']
    search_fields = ['make', 'model', 'product__title']
    list_per_page = 20

    def product_title(self, obj):
        return obj.product.title
    product_title.short_description = "عنوان المنتج"

    def make_model_year(self, obj):
        return "{} {} ({})".format(obj.make, obj.model, obj.year)
    make_model_year.short_description = "السيارة"

    def mileage_display(self, obj):
        return "{:,} كم".format(obj.mileage)
    mileage_display.short_description = "المسافة المقطوعة"

    def fuel_transmission(self, obj):
        fuel_names = {'gasoline': 'بنزين', 'diesel': 'ديزل', 'hybrid': 'هجين', 'electric': 'كهربائي'}
        trans_names = {'automatic': 'أوتوماتيك', 'manual': 'يدوي'}
        return "{} - {}".format(
            fuel_names.get(obj.fuel_type, obj.fuel_type),
            trans_names.get(obj.transmission_type, obj.transmission_type)
        )
    fuel_transmission.short_description = "الوقود والناقل"

    def price_display(self, obj):
        try:
            price_value = float(obj.product.price) if obj.product and obj.product.price else 0
            formatted_price = "{:,.0f}".format(price_value)
        except (ValueError, TypeError):
            formatted_price = "0"
        
        return format_html(
            '<span style="color: #28a745; font-weight: bold;">{} ر.س</span>',
            formatted_price
        )
    price_display.short_description = "السعر"

# Real Estate Admin
@admin.register(RealEstate)
class RealEstateAdmin(admin.ModelAdmin):
    list_display = ['product_title', 'property_type_display', 'area_display', 'rooms_display', 'rent_sale', 'price_display']
    list_filter = ['property_type', 'for_rent', 'is_furnished', 'num_bedrooms']
    search_fields = ['product__title', 'product__description']

    def product_title(self, obj):
        return obj.product.title
    product_title.short_description = "عنوان المنتج"

    def property_type_display(self, obj):
        type_names = {'apartment': 'شقة', 'villa': 'فيلا', 'land': 'أرض', 'commercial': 'تجاري'}
        return type_names.get(obj.property_type, obj.property_type)
    property_type_display.short_description = "نوع العقار"

    def area_display(self, obj):
        return "{:,.0f} م²".format(obj.area_sqm)
    area_display.short_description = "المساحة"

    def rooms_display(self, obj):
        if obj.num_bedrooms and obj.num_bathrooms:
            return "{} غرف، {} حمام".format(obj.num_bedrooms, obj.num_bathrooms)
        return "غير محدد"
    rooms_display.short_description = "الغرف"

    def rent_sale(self, obj):
        return "للإيجار" if obj.for_rent else "للبيع"
    rent_sale.short_description = "نوع العرض"

    def price_display(self, obj):
        suffix = "/شهر" if obj.for_rent else ""
        return str(obj.product.price) + " ر.س" + suffix
    price_display.short_description = "السعر"

# Hotel Booking Admin
@admin.register(HotelBooking)
class HotelBookingAdmin(admin.ModelAdmin):
    list_display = ['hotel_name', 'product_title', 'room_type_display', 'dates_display', 'guests_display', 'price_display']
    list_filter = ['room_type', 'num_guests', 'check_in_date']
    search_fields = ['hotel_name', 'product__title']

    def product_title(self, obj):
        return obj.product.title
    product_title.short_description = "عنوان المنتج"

    def room_type_display(self, obj):
        room_names = {'single': 'فردية', 'double': 'مزدوجة', 'suite': 'جناح', 'family': 'عائلية'}
        return room_names.get(obj.room_type, obj.room_type)
    room_type_display.short_description = "نوع الغرفة"

    def dates_display(self, obj):
        return "{} إلى {}".format(obj.check_in_date, obj.check_out_date)
    dates_display.short_description = "فترة الإقامة"

    def guests_display(self, obj):
        return "{} ضيف/ضيوف".format(obj.num_guests)
    guests_display.short_description = "عدد الضيوف"

    def price_display(self, obj):
        return str(obj.product.price) + " ر.س/ليلة"
    price_display.short_description = "السعر"

# Product Image Admin
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['image_preview', 'product_title', 'is_main', 'created_at']
    list_filter = ['is_main', 'created_at']
    search_fields = ['product__title']

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 8px;" />',
                obj.image.url
            )
        return "لا توجد صورة"
    image_preview.short_description = "الصورة"

    def product_title(self, obj):
        return obj.product.title
    product_title.short_description = "المنتج"

# Customize Admin Site
admin.site.site_header = "إدارة Dalal Alsaudia"
admin.site.site_title = "Dalal Alsaudia"
admin.site.index_title = "لوحة التحكم الرئيسية"
