from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Order
from products.models import Product
from django.db.models import Q

# Create your views here.

@login_required
def create_order(request, product_id):
    """إنشاء طلب جديد"""
    product = get_object_or_404(Product, id=product_id)
    
    # التحقق من أن المنتج متاح
    if product.status != 'active' or not product.is_approved:
        messages.error(request, 'هذا المنتج غير متاح حالياً')
        return redirect('products:detail', pk=product.id)
    
    # التحقق من أن المستخدم ليس صاحب المنتج
    if product.seller == request.user:
        messages.error(request, 'لا يمكنك طلب منتجك')
        return redirect('products:detail', pk=product.id)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        notes = request.POST.get('notes', '')
        
        # إنشاء الطلب
        order = Order.objects.create(
            buyer=request.user,
            seller=product.seller,
            product=product,
            total_amount=product.price * quantity,
            notes=notes
        )
        
        messages.success(request, 'تم إنشاء طلبك بنجاح')
        return redirect('orders:detail', order_id=order.id)
    
    return render(request, 'orders/create_order.html', {'product': product})

@login_required
def order_detail(request, order_id):
    """عرض تفاصيل الطلب"""
    order = Order.objects.filter(
        Q(buyer=request.user) | Q(seller=request.user),
        id=order_id
    ).first()
    
    if not order:
        messages.error(request, 'الطلب غير موجود')
        return redirect('orders:my_orders')
    
    return render(request, 'orders/detail.html', {'order': order})

@login_required
def my_orders(request):
    """عرض طلبات المستخدم"""
    # الطلبات التي قام بها المستخدم كمشتري
    buying_orders = Order.objects.filter(buyer=request.user).order_by('-order_date')
    
    # الطلبات التي استقبلها المستخدم كبائع
    selling_orders = Order.objects.filter(seller=request.user).order_by('-order_date')
    
    # حساب الإحصائيات
    all_orders = Order.objects.filter(Q(buyer=request.user) | Q(seller=request.user))
    total_orders = all_orders.count()
    pending_orders = all_orders.filter(status='pending').count()
    confirmed_orders = all_orders.filter(status='confirmed').count()
    completed_orders = all_orders.filter(status='completed').count()
    
    return render(request, 'orders/my_orders.html', {
        'buying_orders': buying_orders,
        'selling_orders': selling_orders,
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'confirmed_orders': confirmed_orders,
        'completed_orders': completed_orders,
    })

@login_required
def update_order_status(request, order_id):
    """تحديث حالة الطلب"""
    order = get_object_or_404(Order, id=order_id, seller=request.user)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        valid_statuses = ['pending', 'confirmed', 'cancelled', 'completed']
        
        if new_status in valid_statuses:
            order.status = new_status
            order.save()
            
            messages.success(request, 'تم تحديث حالة الطلب بنجاح')
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'حالة غير صحيحة'})
    
    return JsonResponse({'success': False, 'error': 'طريقة غير مسموحة'})

@login_required
def cancel_order(request, order_id):
    """إلغاء الطلب"""
    order = get_object_or_404(Order, id=order_id, buyer=request.user)
    
    # يمكن إلغاء الطلب فقط إذا كان في حالة pending أو confirmed
    if order.status not in ['pending', 'confirmed']:
        messages.error(request, 'لا يمكن إلغاء هذا الطلب')
        return redirect('orders:detail', order_id=order.id)
    
    if request.method == 'POST':
        order.status = 'cancelled'
        order.save()
        
        messages.success(request, 'تم إلغاء الطلب بنجاح')
        return redirect('orders:my_orders')
    
    return render(request, 'orders/cancel_order.html', {'order': order})

@login_required
def order_history(request):
    """تاريخ الطلبات"""
    # الطلبات المكتملة والملغية
    completed_orders = Order.objects.filter(
        Q(buyer=request.user) | Q(seller=request.user),
        status__in=['completed', 'cancelled']
    ).order_by('-order_date')
    
    return render(request, 'orders/history.html', {
        'orders': completed_orders
    })
