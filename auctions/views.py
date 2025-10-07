# auctions/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Max
from .models import Auction, Bid
from products.models import Product
from decimal import Decimal

@login_required
def auction_list(request):
    """عرض قائمة المزادات النشطة"""
    active_auctions = Auction.objects.filter(
        status='active',
        end_time__gt=timezone.now()
    ).order_by('end_time')
    
    return render(request, 'auctions/auction_list.html', {
        'auctions': active_auctions
    })

@login_required
def auction_detail(request, auction_id):
    """عرض تفاصيل المزاد"""
    auction = get_object_or_404(Auction, id=auction_id)
    
    # جلب المزايدات مرتبة حسب المبلغ
    bids = auction.bids.order_by('-amount', '-timestamp')
    
    # التحقق من انتهاء المزاد
    if auction.end_time <= timezone.now() and auction.status == 'active':
        auction.status = 'closed'
        auction.save()
        
        # تحديد الفائز
        if bids.exists():
            winning_bid = bids.first()
            auction.highest_bidder = winning_bid.bidder
            auction.current_bid = winning_bid.amount
            auction.save()
    
    user_highest_bid = None
    if request.user.is_authenticated:
        user_bids = bids.filter(bidder=request.user)
        if user_bids.exists():
            user_highest_bid = user_bids.first()
    
    return render(request, 'auctions/auction_detail.html', {
        'auction': auction,
        'bids': bids[:10],  # عرض آخر 10 مزايدات
        'user_highest_bid': user_highest_bid,
        'time_remaining': auction.end_time - timezone.now() if auction.end_time > timezone.now() else None
    })

@login_required
def create_auction(request, product_id):
    """إنشاء مزاد جديد لمنتج"""
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    
    # التحقق من عدم وجود مزاد مسبق
    if hasattr(product, 'auction'):
        messages.error(request, 'يوجد مزاد مسبق لهذا المنتج')
        return redirect('products:detail', product_id=product.id)
    
    if request.method == 'POST':
        starting_bid = request.POST.get('starting_bid')
        duration_hours = int(request.POST.get('duration_hours', 24))
        
        try:
            starting_bid = Decimal(starting_bid)
            end_time = timezone.now() + timezone.timedelta(hours=duration_hours)
            
            auction = Auction.objects.create(
                product=product,
                start_time=timezone.now(),
                end_time=end_time,
                starting_bid=starting_bid,
                current_bid=starting_bid
            )
            
            messages.success(request, 'تم إنشاء المزاد بنجاح')
            return redirect('auctions:detail', auction_id=auction.id)
            
        except (ValueError, TypeError):
            messages.error(request, 'يرجى إدخال مبلغ صحيح')
    
    return render(request, 'auctions/create_auction.html', {
        'product': product
    })

@login_required
def place_bid(request, auction_id):
    """وضع مزايدة جديدة"""
    auction = get_object_or_404(Auction, id=auction_id)
    
    # التحقق من صحة المزاد
    if auction.status != 'active':
        return JsonResponse({'success': False, 'error': 'المزاد غير نشط'})
    
    if auction.end_time <= timezone.now():
        return JsonResponse({'success': False, 'error': 'انتهى وقت المزاد'})
    
    if auction.product.seller == request.user:
        return JsonResponse({'success': False, 'error': 'لا يمكنك المزايدة على منتجك'})
    
    if request.method == 'POST':
        try:
            bid_amount = Decimal(request.POST.get('amount'))
            
            # التحقق من أن المزايدة أعلى من الحالية
            minimum_bid = auction.current_bid + Decimal('10')  # زيادة 10 ريال على الأقل
            
            if bid_amount < minimum_bid:
                return JsonResponse({
                    'success': False, 
                    'error': f'يجب أن تكون المزايدة أعلى من {minimum_bid} ريال'
                })
            
            # إنشاء المزايدة
            bid = Bid.objects.create(
                auction=auction,
                bidder=request.user,
                amount=bid_amount
            )
            
            # تحديث المزاد
            auction.current_bid = bid_amount
            auction.highest_bidder = request.user
            auction.save()
            
            return JsonResponse({
                'success': True,
                'message': 'تم وضع المزايدة بنجاح',
                'new_amount': str(bid_amount),
                'bidder': request.user.username
            })
            
        except (ValueError, TypeError):
            return JsonResponse({'success': False, 'error': 'مبلغ غير صحيح'})
    
    return JsonResponse({'success': False, 'error': 'طريقة غير مسموحة'})

@login_required
def my_auctions(request):
    """عرض مزادات المستخدم"""
    # المزادات التي أنشأها المستخدم
    created_auctions = Auction.objects.filter(
        product__seller=request.user
    ).order_by('-created_at')
    
    # المزادات التي شارك فيها المستخدم
    participated_auctions = Auction.objects.filter(
        bids__bidder=request.user
    ).distinct().order_by('-created_at')
    
    return render(request, 'auctions/my_auctions.html', {
        'created_auctions': created_auctions,
        'participated_auctions': participated_auctions
    })

@login_required
def cancel_auction(request, auction_id):
    """إلغاء المزاد"""
    auction = get_object_or_404(
        Auction, 
        id=auction_id, 
        product__seller=request.user,
        status='active'
    )
    
    if request.method == 'POST':
        auction.status = 'cancelled'
        auction.save()
        messages.success(request, 'تم إلغاء المزاد بنجاح')
        return redirect('auctions:my_auctions')
    
    return render(request, 'auctions/cancel_auction.html', {
        'auction': auction
    })

