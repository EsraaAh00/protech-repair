# products/admin.py
from django.contrib import admin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from .models import (
    ProductCategory, Product, ProductImage,
    OpenerSpecifications, DoorSpecifications
)
from .scraper import scrape_liftmaster_products
from django.utils.text import slugify


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
    change_list_template = "admin/products/product_changelist.html"
    
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
        ('الصورة والملفات / Image & Files', {
            'fields': ('image', 'pdf_url')
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
    
    def get_urls(self):
        """Add custom URLs for scraping"""
        urls = super().get_urls()
        custom_urls = [
            path('scrape-liftmaster/', self.admin_site.admin_view(self.scrape_liftmaster_view), name='products_scrape_liftmaster'),
        ]
        return custom_urls + urls
    
    def import_liftmaster_products(self):
        """Import LiftMaster products manually"""
        from .models import ProductCategory
        
        # Get or create category
        category, _ = ProductCategory.objects.get_or_create(
            name_en='Garage Door Openers',
            defaults={
                'name': 'فتاحات أبواب الجراج',
                'slug': 'garage-door-openers',
                'is_active': True,
            }
        )
        
        # List of products
        products_data = [
            {
                'name': 'LM-W8ME Sectional Garage Door Opener',
                'model_number': 'LM-W8ME',
                'description': 'فتاحة أبواب جراج قطاعية من LiftMaster - موديل LM-W8ME. فتاحة قوية وموثوقة مصممة للأبواب القطاعية، توفر أداءً ممتازاً وسهولة في التشغيل.',
                'category': 'Sectional Garage Door',
                'features': 'محرك قوي وموثوق\nمناسب للأبواب القطاعية\nسهل التركيب والصيانة\nضمان من الشركة المصنعة',
            },
            {
                'name': 'LM3800TXSA Sectional Garage Door Opener',
                'model_number': 'LM3800TXSA',
                'description': 'فتاحة أبواب جراج قطاعية من LiftMaster - موديل LM3800TXSA. موديل متطور بتقنية حديثة لضمان الأداء الأمثل.',
                'category': 'Sectional Garage Door',
                'features': 'تقنية متقدمة\nأداء عالي\nموثوقية ممتازة\nسهل الاستخدام',
            },
            {
                'name': 'LM80EV DC Sectional Garage Door Opener',
                'model_number': 'LM80EV',
                'description': 'فتاحة أبواب جراج قطاعية DC من LiftMaster - موديل LM80EV. محرك DC بكفاءة طاقة عالية وأداء هادئ.',
                'category': 'Sectional Garage Door',
                'features': 'محرك DC موفر للطاقة\nتشغيل هادئ\nبطارية احتياطية\nكفاءة عالية',
            },
            {
                'name': 'LM100EV Sectional Garage Door Opener',
                'model_number': 'LM100EV',
                'description': 'فتاحة أبواب جراج قطاعية من LiftMaster - موديل LM100EV. حل مثالي للأبواب القطاعية متوسطة الحجم.',
                'category': 'Sectional Garage Door',
                'features': 'مناسب للأبواب متوسطة الحجم\nأداء موثوق\nسهل التركيب\nصيانة قليلة',
            },
            {
                'name': 'LM130EV Sectional Garage Door Opener',
                'model_number': 'LM130EV',
                'description': 'فتاحة أبواب جراج قطاعية من LiftMaster - موديل LM130EV. موديل قوي مصمم للأبواب الثقيلة.',
                'category': 'Sectional Garage Door',
                'features': 'قوة رفع عالية\nمناسب للأبواب الثقيلة\nمتانة استثنائية\nضمان ممتد',
            },
            {
                'name': 'LM555EVGBSA Roller Garage Opener Weather Resistant',
                'model_number': 'LM555EVGBSA',
                'description': 'فتاحة أبواب رولر مقاومة للطقس من LiftMaster - موديل LM555EVGBSA. مصممة خصيصاً لتحمل الظروف الجوية القاسية.',
                'category': 'Roller Garage Door',
                'features': 'مقاومة للطقس والرطوبة\nمناسب لأبواب الرولر\nحماية من الغبار والماء\nمتانة عالية',
            },
        ]
        
        imported = 0
        skipped = 0
        errors = 0
        
        for product_data in products_data:
            try:
                # Check if exists
                existing = Product.objects.filter(
                    model_number=product_data['model_number']
                ).first()
                
                if existing:
                    skipped += 1
                    continue
                
                # Create product
                Product.objects.create(
                    name=product_data['name'],
                    name_en=product_data['name'],
                    slug=slugify(product_data['name']),
                    model_number=product_data['model_number'],
                    category=category,
                    product_type='opener',
                    brand='LiftMaster',
                    description=product_data['description'],
                    short_description=f"{product_data['category']} - {product_data['model_number']}",
                    features=product_data.get('features', ''),
                    is_active=True,
                )
                
                imported += 1
                
            except Exception as e:
                errors += 1
        
        return {
            'success': True,
            'imported': imported,
            'skipped': skipped,
            'errors': errors
        }
    
    def scrape_liftmaster_view(self, request):
        """View to handle LiftMaster import"""
        if request.method == 'POST':
            try:
                # Import products directly
                result = self.import_liftmaster_products()
                
                if result['imported'] > 0:
                    self.message_user(
                        request,
                        f"✅ تم استيراد المنتجات بنجاح! المضاف: {result['imported']}, المتخطى: {result['skipped']}",
                        messages.SUCCESS
                    )
                    self.message_user(
                        request,
                        "💡 يمكنك الآن إضافة الصور والأسعار لكل منتج من خلال تعديل المنتج.",
                        messages.INFO
                    )
                elif result['skipped'] > 0:
                    self.message_user(
                        request,
                        f"⏭️ جميع المنتجات موجودة بالفعل. المتخطى: {result['skipped']}",
                        messages.INFO
                    )
                else:
                    self.message_user(
                        request,
                        "⚠️ لم يتم استيراد أي منتجات جديدة.",
                        messages.WARNING
                    )
                
                if result['errors'] > 0:
                    self.message_user(
                        request,
                        f"⚠️ حدثت {result['errors']} أخطاء أثناء الاستيراد.",
                        messages.WARNING
                    )
                    
            except Exception as e:
                self.message_user(
                    request,
                    f"❌ حدث خطأ أثناء استيراد المنتجات: {str(e)}",
                    messages.ERROR
                )
            
            return redirect('..')
        
        # GET request - show confirmation page
        context = {
            **self.admin_site.each_context(request),
            'title': 'استيراد منتجات LiftMaster',
            'opts': self.model._meta,
        }
        return render(request, 'admin/products/scrape_confirm.html', context)


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
