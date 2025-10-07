from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg
from .models import Review
from products.models import Product
from django.http import JsonResponse

# Create your views here.

@login_required
def add_review(request, product_id):
    """إضافة تقييم لمنتج"""
    product = get_object_or_404(Product, id=product_id)
    
    # التحقق من عدم تقييم المستخدم للمنتج مسبقاً
    existing_review = Review.objects.filter(user=request.user, product=product).first()
    if existing_review:
        messages.error(request, 'لقد قمت بتقييم هذا المنتج مسبقاً')
        return redirect('products:detail', pk=product.id)
    
    # التحقق من أن المستخدم ليس صاحب المنتج
    if product.seller == request.user:
        messages.error(request, 'لا يمكنك تقييم منتجك')
        return redirect('products:detail', pk=product.id)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '')
        
        try:
            rating = int(rating)
            if 1 <= rating <= 5:
                Review.objects.create(
                    user=request.user,
                    product=product,
                    rating=rating,
                    comment=comment
                )
                messages.success(request, 'تم إضافة تقييمك بنجاح')
                return redirect('products:detail', pk=product.id)
            else:
                messages.error(request, 'التقييم يجب أن يكون بين 1 و 5')
        except ValueError:
            messages.error(request, 'تقييم غير صحيح')
    
    return render(request, 'reviews/add_review.html', {'product': product})

def product_reviews(request, product_id):
    """عرض تقييمات المنتج"""
    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(product=product).order_by('-created_at')
    
    # حساب متوسط التقييم
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    
    context = {
        'product': product,
        'reviews': reviews,
        'avg_rating': round(avg_rating, 1) if avg_rating else 0,
        'total_reviews': reviews.count()
    }
    
    return render(request, 'reviews/product_reviews.html', context)

@login_required
def my_reviews(request):
    """عرض تقييمات المستخدم"""
    reviews = Review.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'reviews/my_reviews.html', {'reviews': reviews})

@login_required
def edit_review(request, review_id):
    """تعديل تقييم"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment', '')
        
        try:
            rating = int(rating)
            if 1 <= rating <= 5:
                review.rating = rating
                review.comment = comment
                review.save()
                messages.success(request, 'تم تحديث تقييمك بنجاح')
                return redirect('reviews:my_reviews')
            else:
                messages.error(request, 'التقييم يجب أن يكون بين 1 و 5')
        except ValueError:
            messages.error(request, 'تقييم غير صحيح')
    
    return render(request, 'reviews/edit_review.html', {'review': review})

@login_required
def delete_review(request, review_id):
    """حذف تقييم"""
    review = get_object_or_404(Review, id=review_id, user=request.user)
    
    if request.method == 'POST':
        product_id = review.product.id
        review.delete()
        messages.success(request, 'تم حذف تقييمك بنجاح')
        return redirect('products:detail', pk=product_id)
    
    return render(request, 'reviews/delete_review.html', {'review': review})
