from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class CustomUserAdmin(BaseUserAdmin):
    """Enhanced User Admin with custom fields"""
    list_display = [
        'username', 'email', 'first_name', 'last_name', 
        'is_seller_display', 'is_staff', 'is_active', 'date_joined'
    ]
    list_filter = [
        'is_active', 'is_staff', 'is_superuser', 'is_seller', 
        'is_admin_verified', 'date_joined', 'last_login'
    ]
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone_number']
    ordering = ['-date_joined']
    
    fieldsets = (
        ('User Information', {
            'fields': ('username', 'email', 'password'),
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'phone_number', 'address', 'profile_picture'),
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser',
                'is_seller', 'is_admin_verified',
                'groups', 'user_permissions'
            ),
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined'),
        }),
    )
    
    add_fieldsets = (
        ('Create New User', {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
        ('Personal Info', {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name', 'phone_number'),
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_seller'),
        }),
    )
    
    readonly_fields = ('last_login', 'date_joined')
    
    def is_seller_display(self, obj):
        """Display seller status with badge"""
        if obj.is_seller:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px;">✓ Seller</span>'
            )
        return format_html(
            '<span style="background: #6c757d; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px;">User</span>'
        )
    is_seller_display.short_description = 'Account Type'

# Note: User will be registered in core/admin.py with admin_site
