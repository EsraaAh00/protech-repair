#!/usr/bin/env python
import os
import django

# إعداد Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# إنشاء مستخدم إداري
admin_user, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@dalalsaudi.com',
        'first_name': 'مدير',
        'last_name': 'النظام',
        'is_staff': True,
        'is_superuser': True,
        'is_active': True
    }
)

if created:
    admin_user.set_password('admin123')
    admin_user.save()
    print('✅ تم إنشاء المستخدم الإداري بنجاح!')
    print('اسم المستخدم: admin')
    print('كلمة المرور: admin123')
else:
    print('ℹ️ المستخدم الإداري موجود مسبقاً')
    print('اسم المستخدم: admin')
    print('كلمة المرور: admin123') 