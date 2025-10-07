# admin_panel/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.db.models import Count, Q
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from products.models import Product, Car, RealEstate, HotelBooking
from users.models import User
from auctions.models import Auction
from reviews.models import Review
from orders.models import Order
from messaging.models import Message

@staff_member_required
def admin_dashboard(request):
    """لوحة التحكم الرئيسية للمسؤول"""
    
    # إحصائيات عامة
    total_products = Product.objects.count()
    pending_products = Product.objects.filter(status='pending_approval').count()
    active_products = Product.objects.filter(status='active').count()
    total_users = User.objects.count()
    new_users_today = User.objects.filter(date_joined__date=timezone.now().date()).count()
    
    # إحصائيات المزادات
    active_auctions = Auction.objects.filter(status='active').count()
    total_auctions = Auction.objects.count()
    
    # إحصائيات الطلبات
    pending_orders = Order.objects.filter(status='pending').count()
    completed_orders = Order.objects.filter(status='completed').count()
    
    # المنتجات الأحدث المعلقة للموافقة
    recent_pending = Product.objects.filter(
        status='pending_approval'
    ).order_by('-created_at')[:5]
    
    # المستخدمين الجدد
    recent_users = User.objects.order_by('-date_joined')[:5]
    
    # إحصائيات الأسبوع الماضي
    week_ago = timezone.now() - timedelta(days=7)
    products_this_week = Product.objects.filter(created_at__gte=week_ago).count()
    users_this_week = User.objects.filter(date_joined__gte=week_ago).count()
    
    context = {
        'total_products': total_products,
        'pending_products': pending_products,
        'active_products': active_products,
        'total_users': total_users,
        'new_users_today': new_users_today,
        'active_auctions': active_auctions,
        'total_auctions': total_auctions,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'recent_pending': recent_pending,
        'recent_users': recent_users,
        'products_this_week': products_this_week,
        'users_this_week': users_this_week,
    }
    
    return render(request, 'admin_panel/dashboard.html', context)

@staff_member_required
def pending_products(request):
    """عرض المنتجات المعلقة للموافقة"""
    
    products = Product.objects.filter(
        status='pending_approval'
    ).select_related('seller', 'category').order_by('-created_at')
    
    # تصفية حسب الفئة
    category = request.GET.get('category')
    if category:
        products = products.filter(category__slug=category)
    
    # تصفية حسب البائع
    seller = request.GET.get('seller')
    if seller:
        products = products.filter(seller__username__icontains=seller)
    
    return render(request, 'admin_panel/pending_products.html', {
        'products': products,
        'selected_category': category,
        'selected_seller': seller,
    })

@staff_member_required
def approve_product(request, product_id):
    """الموافقة على منتج"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        product.status = 'active'
        product.is_approved = True
        product.save()
        
        messages.success(request, f'تمت الموافقة على المنتج "{product.title}" بنجاح')
        
        # إرسال إشعار للبائع (يمكن تطويره لاحقاً)
        
        return JsonResponse({'success': True, 'message': 'تمت الموافقة بنجاح'})
    
    return JsonResponse({'success': False, 'error': 'طريقة غير مسموحة'})

@staff_member_required
def reject_product(request, product_id):
    """رفض منتج"""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        
        product.status = 'cancelled'
        product.save()
        
        # يمكن حفظ سبب الرفض في نموذج منفصل
        
        messages.success(request, f'تم رفض المنتج "{product.title}"')
        
        return JsonResponse({'success': True, 'message': 'تم الرفض بنجاح'})
    
    return JsonResponse({'success': False, 'error': 'طريقة غير مسموحة'})

@staff_member_required
def product_detail_admin(request, product_id):
    """عرض تفاصيل المنتج للمسؤول"""
    product = get_object_or_404(Product, id=product_id)
    
    # جلب التفاصيل الإضافية حسب نوع المنتج
    product_details = None
    if hasattr(product, 'car_details'):
        product_details = product.car_details
    elif hasattr(product, 'realestate_details'):
        product_details = product.realestate_details
    elif hasattr(product, 'hotel_details'):
        product_details = product.hotel_details
    
    # جلب الرسائل المتعلقة بالمنتج
    messages_count = Message.objects.filter(product=product).count()
    
    # جلب المزاد إن وجد
    auction = None
    if hasattr(product, 'auction'):
        auction = product.auction
    
    context = {
        'product': product,
        'product_details': product_details,
        'messages_count': messages_count,
        'auction': auction,
    }
    
    return render(request, 'admin_panel/product_detail.html', context)

@staff_member_required
def users_management(request):
    """إدارة المستخدمين"""
    
    users = User.objects.all().order_by('-date_joined')
    
    # تصفية حسب نوع المستخدم
    user_type = request.GET.get('type')
    if user_type == 'sellers':
        users = users.filter(is_seller=True)
    elif user_type == 'verified':
        users = users.filter(is_admin_verified=True)
    elif user_type == 'staff':
        users = users.filter(is_staff=True)
    
    # البحث
    search = request.GET.get('search')
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    return render(request, 'admin_panel/users_management.html', {
        'users': users,
        'selected_type': user_type,
        'search_query': search,
    })

@staff_member_required
def verify_user(request, user_id):
    """التحقق من المستخدم"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user.is_admin_verified = True
        user.save()
        
        messages.success(request, f'تم التحقق من المستخدم {user.username} بنجاح')
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'طريقة غير مسموحة'})

@staff_member_required
def suspend_user(request, user_id):
    """تعليق المستخدم"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user.is_active = False
        user.save()
        
        messages.success(request, f'تم تعليق المستخدم {user.username}')
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'طريقة غير مسموحة'})

@staff_member_required
def reports_analytics(request):
    """التقارير والإحصائيات"""
    
    # إحصائيات المنتجات حسب الفئة
    products_by_category = Product.objects.values('category__name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # إحصائيات المنتجات حسب الحالة
    products_by_status = Product.objects.values('status').annotate(
        count=Count('id')
    )
    
    # إحصائيات المستخدمين الجدد (آخر 30 يوم)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    new_users_monthly = User.objects.filter(
        date_joined__gte=thirty_days_ago
    ).extra(
        select={'day': 'date(date_joined)'}
    ).values('day').annotate(count=Count('id')).order_by('day')
    
    # أكثر البائعين نشاطاً
    top_sellers = User.objects.filter(is_seller=True).annotate(
        products_count=Count('products')
    ).order_by('-products_count')[:10]
    
    # المنتجات الأكثر مشاهدة
    most_viewed = Product.objects.filter(
        status='active'
    ).order_by('-views_count')[:10]
    
    context = {
        'products_by_category': products_by_category,
        'products_by_status': products_by_status,
        'new_users_monthly': new_users_monthly,
        'top_sellers': top_sellers,
        'most_viewed': most_viewed,
    }
    
    return render(request, 'admin_panel/reports.html', context)

@staff_member_required
def system_settings(request):
    """إعدادات النظام"""
    
    if request.method == 'POST':
        # معالجة تحديث الإعدادات
        # يمكن إضافة نموذج للإعدادات لاحقاً
        messages.success(request, 'تم تحديث الإعدادات بنجاح')
        return redirect('admin_panel:settings')
    
    return render(request, 'admin_panel/settings.html')

@staff_member_required
def bulk_actions(request):
    """الإجراءات المجمعة"""
    
    if request.method == 'POST':
        action = request.POST.get('action')
        product_ids = request.POST.getlist('product_ids')
        
        if not product_ids:
            return JsonResponse({'success': False, 'error': 'لم يتم اختيار منتجات'})
        
        products = Product.objects.filter(id__in=product_ids)
        
        if action == 'approve':
            products.update(status='active', is_approved=True)
            message = f'تمت الموافقة على {len(product_ids)} منتج'
        elif action == 'reject':
            products.update(status='cancelled')
            message = f'تم رفض {len(product_ids)} منتج'
        elif action == 'hide':
            products.update(status='hidden')
            message = f'تم إخفاء {len(product_ids)} منتج'
        else:
            return JsonResponse({'success': False, 'error': 'إجراء غير صحيح'})
        
        return JsonResponse({'success': True, 'message': message})
    
    return JsonResponse({'success': False, 'error': 'طريقة غير مسموحة'})

