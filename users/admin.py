from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display = [
        'username_with_status', 'user_info', 'activity_stats', 
        'registration_info', 'last_login_display', 'actions_display'
    ]
    list_filter = [
        'is_active', 'is_staff', 'is_superuser', 'date_joined', 'last_login'
    ]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    list_per_page = 25
    date_hierarchy = 'date_joined'
    ordering = ['-date_joined']
    
    fieldsets = (
        ('معلومات المستخدم', {
            'fields': ('username', 'email', 'password'),
            'classes': ('wide',)
        }),
        ('البيانات الشخصية', {
            'fields': ('first_name', 'last_name'),
            'classes': ('wide',)
        }),
        ('الصلاحيات', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'groups', 'user_permissions'
            ),
            'classes': ('collapse',)
        }),
        ('التواريخ المهمة', {
            'fields': ('last_login', 'date_joined'),
            'classes': ('collapse',)
        })
    )
    
    add_fieldsets = (
        ('إنشاء مستخدم جديد', {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
        ('البيانات الشخصية', {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name'),
        }),
        ('الصلاحيات', {
            'classes': ('collapse',),
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
    )
    
    readonly_fields = ('last_login', 'date_joined')
    
    actions = ['activate_users', 'deactivate_users', 'make_staff']

    def username_with_status(self, obj):
        # تحديد حالة المستخدم
        if obj.is_superuser:
            badge = '<span style="background: #dc3545; color: white; padding: 2px 6px; border-radius: 10px; font-size: 10px; margin-right: 5px;">مدير عام</span>'
        elif obj.is_staff:
            badge = '<span style="background: #007bff; color: white; padding: 2px 6px; border-radius: 10px; font-size: 10px; margin-right: 5px;">موظف</span>'
        else:
            badge = '<span style="background: #28a745; color: white; padding: 2px 6px; border-radius: 10px; font-size: 10px; margin-right: 5px;">عضو</span>'
        
        status_color = '#28a745' if obj.is_active else '#dc3545'
        status_icon = '🟢' if obj.is_active else '🔴'
        
        return format_html(
            '<div style="display: flex; align-items: center;">'
            '<span style="font-size: 16px; margin-left: 8px;">{}</span>'
            '<div>'
            '<strong style="color: {};">{}</strong><br>'
            '{}'
            '</div>'
            '</div>',
            status_icon, status_color, obj.username, badge
        )
    username_with_status.short_description = "اسم المستخدم"

    def user_info(self, obj):
        full_name = obj.get_full_name() or "غير محدد"
        return format_html(
            '<div>'
            '<strong>{}</strong><br>'
            '<small style="color: #666;">{}</small>'
            '</div>',
            full_name, obj.email
        )
    user_info.short_description = "المعلومات الشخصية"

    def activity_stats(self, obj):
        # حساب إحصائيات النشاط
        products_count = obj.products.count()
        active_products = obj.products.filter(status='active').count()
        sold_products = obj.products.filter(status='sold').count()
        
        return format_html(
            '<div style="font-size: 12px;">'
            '<div><strong>منتجات:</strong> <span style="color: #007bff;">{}</span></div>'
            '<div><strong>نشطة:</strong> <span style="color: #28a745;">{}</span></div>'
            '<div><strong>مباعة:</strong> <span style="color: #6c757d;">{}</span></div>'
            '</div>',
            products_count, active_products, sold_products
        )
    activity_stats.short_description = "إحصائيات النشاط"

    def registration_info(self, obj):
        # حساب عدد الأيام منذ التسجيل
        days_since_joined = (timezone.now() - obj.date_joined).days
        
        if days_since_joined == 0:
            period = "اليوم"
        elif days_since_joined < 30:
            period = "{} يوم".format(days_since_joined)
        elif days_since_joined < 365:
            months = days_since_joined // 30
            period = "{} شهر".format(months)
        else:
            years = days_since_joined // 365
            period = "{} سنة".format(years)
        
        return format_html(
            '<div>'
            '<strong>{}</strong><br>'
            '<small style="color: #666;">منذ {}</small>'
            '</div>',
            obj.date_joined.strftime('%Y/%m/%d'), period
        )
    registration_info.short_description = "تاريخ التسجيل"

    def last_login_display(self, obj):
        if obj.last_login:
            # حساب آخر تسجيل دخول
            time_diff = timezone.now() - obj.last_login
            
            if time_diff.days == 0:
                if time_diff.seconds < 3600:
                    minutes = time_diff.seconds // 60
                    last_seen = "منذ {} دقيقة".format(minutes)
                    color = "#28a745"
                else:
                    hours = time_diff.seconds // 3600
                    last_seen = "منذ {} ساعة".format(hours)
                    color = "#ffc107"
            elif time_diff.days < 7:
                last_seen = "منذ {} يوم".format(time_diff.days)
                color = "#17a2b8"
            else:
                last_seen = obj.last_login.strftime('%Y/%m/%d')
                color = "#6c757d"
            
            return format_html(
                '<div>'
                '<strong style="color: {};">{}</strong><br>'
                '<small style="color: #666;">{}</small>'
                '</div>',
                color, obj.last_login.strftime('%H:%M'), last_seen
            )
        return format_html('<span style="color: #dc3545;">لم يسجل دخول مطلقاً</span>')
    last_login_display.short_description = "آخر تسجيل دخول"

    def actions_display(self, obj):
        actions = []
        
        if not obj.is_active:
            actions.append(
                '<button onclick="activateUser({})" style="background: #28a745; color: white; border: none; padding: 4px 8px; border-radius: 4px; font-size: 12px; cursor: pointer;">تفعيل</button>'.format(obj.id)
            )
        else:
            actions.append(
                '<button onclick="deactivateUser({})" style="background: #dc3545; color: white; border: none; padding: 4px 8px; border-radius: 4px; font-size: 12px; cursor: pointer;">إلغاء التفعيل</button>'.format(obj.id)
            )
        
        return format_html('<div style="display: flex; gap: 5px;">{}</div>', ''.join(actions))
    actions_display.short_description = "إجراءات"

    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, 'تم تفعيل {} مستخدم.'.format(updated))
    activate_users.short_description = "تفعيل المستخدمين المحددين"

    def deactivate_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, 'تم إلغاء تفعيل {} مستخدم.'.format(updated))
    deactivate_users.short_description = "إلغاء تفعيل المستخدمين المحددين"

    def make_staff(self, request, queryset):
        updated = queryset.update(is_staff=True)
        self.message_user(request, 'تم منح صلاحيات الموظف لـ {} مستخدم.'.format(updated))
    make_staff.short_description = "منح صلاحيات الموظف"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related().prefetch_related('products')

    class Media:
        js = ('admin/js/user_admin.js',)
        css = {
            'all': ('admin/css/user_admin.css',)
        }
