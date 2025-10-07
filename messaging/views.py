# messaging/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.db.models import Q
from .models import Message, Conversation
from products.models import Product
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

User = get_user_model()

@login_required
def conversations_list(request):
    """عرض قائمة المحادثات للمستخدم"""
    conversations = Conversation.objects.filter(
        participants=request.user
    ).order_by('-updated_at')
    
    return render(request, 'messaging/conversations_list.html', {
        'conversations': conversations
    })

@login_required
def inbox(request):
    """عرض صندوق الوارد للمستخدم"""
    conversations = Conversation.objects.filter(
        participants=request.user
    ).order_by('-updated_at')
    
    return render(request, 'messaging/inbox.html', {
        'conversations': conversations
    })

@login_required
def conversation_detail(request, conversation_id):
    """عرض تفاصيل المحادثة"""
    conversation = get_object_or_404(
        Conversation, 
        id=conversation_id, 
        participants=request.user
    )
    
    # تحديد الرسائل كمقروءة
    Message.objects.filter(
        conversation=conversation,
        receiver=request.user,
        is_read=False
    ).update(is_read=True)
    
    # جلب جميع الرسائل في هذه المحادثة
    messages_list = conversation.messages.all().order_by('timestamp')
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            # تحديد المستقبل (الطرف الآخر في المحادثة)
            other_participant = conversation.participants.exclude(id=request.user.id).first()
            
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                receiver=other_participant,
                content=content,
                product=conversation.product
            )
            
            conversation.save()  # تحديث updated_at
            return redirect('messaging:conversation_detail', conversation_id=conversation.id)
    
    return render(request, 'messaging/conversation_detail.html', {
        'conversation': conversation,
        'messages': messages_list
    })

@login_required
def start_conversation(request, product_id):
    """بدء محادثة جديدة حول منتج"""
    product = get_object_or_404(Product, id=product_id)
    
    if product.seller == request.user:
        messages.error(request, 'لا يمكنك بدء محادثة مع نفسك')
        return redirect('products:detail', product_id=product.id)
    
    # البحث عن محادثة موجودة
    conversation = Conversation.objects.filter(
        participants=request.user,
        product=product
    ).filter(participants=product.seller).first()
    
    if not conversation:
        # إنشاء محادثة جديدة
        conversation = Conversation.objects.create(product=product)
        conversation.participants.add(request.user, product.seller)
    
    return redirect('messaging:conversation_detail', conversation_id=conversation.id)

@login_required
def send_message(request):
    """إرسال رسالة"""
    if request.method == 'POST':
        conversation_id = request.POST.get('conversation_id')
        content = request.POST.get('content')
        
        try:
            conversation = Conversation.objects.get(id=conversation_id, participants=request.user)
            other_participant = conversation.participants.exclude(id=request.user.id).first()
            
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                receiver=other_participant,
                content=content,
                product=conversation.product
            )
            
            conversation.save()  # تحديث updated_at
            return JsonResponse({'success': True})
            
        except Conversation.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'المحادثة غير موجودة'})
    
    return JsonResponse({'success': False, 'error': 'طريقة غير مسموحة'})

@login_required
def send_message_ajax(request):
    """إرسال رسالة عبر AJAX"""
    if request.method == 'POST':
        conversation_id = request.POST.get('conversation_id')
        receiver_id = request.POST.get('receiver_id')
        content = request.POST.get('content')
        
        try:
            conversation = Conversation.objects.get(id=conversation_id, participants=request.user)
            receiver = User.objects.get(id=receiver_id)
            
            message = Message.objects.create(
                conversation=conversation,
                sender=request.user,
                receiver=receiver,
                content=content,
                product=conversation.product
            )
            
            return JsonResponse({
                'success': True,
                'message': {
                    'id': message.id,
                    'content': message.content,
                    'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M'),
                    'sender': message.sender.username
                }
            })
        except (User.DoesNotExist, Conversation.DoesNotExist):
            return JsonResponse({'success': False, 'error': 'بيانات غير صحيحة'})
    
    return JsonResponse({'success': False, 'error': 'طريقة غير مسموحة'})

@login_required
def mark_as_read(request):
    """تحديد الرسائل كمقروءة"""
    if request.method == 'POST':
        conversation_id = request.POST.get('conversation_id')
        
        try:
            conversation = Conversation.objects.get(id=conversation_id, participants=request.user)
            Message.objects.filter(
                conversation=conversation,
                receiver=request.user,
                is_read=False
            ).update(is_read=True)
            
            return JsonResponse({'success': True})
            
        except Conversation.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'المحادثة غير موجودة'})
    
    return JsonResponse({'success': False, 'error': 'طريقة غير مسموحة'})

@csrf_exempt
@require_http_methods(["POST"])
def mark_messages_read_admin(request):
    """تحديد جميع رسائل المحادثة كمقروءة من admin panel"""
    try:
        data = json.loads(request.body)
        conversation_id = data.get('conversation_id')
        
        if not conversation_id:
            return JsonResponse({'success': False, 'error': 'معرف المحادثة مطلوب'})
        
        # التحقق من وجود المحادثة
        try:
            conversation = Conversation.objects.get(pk=conversation_id)
        except Conversation.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'المحادثة غير موجودة'})
        
        # تحديد جميع الرسائل كمقروءة
        updated_count = conversation.messages.filter(is_read=False).update(is_read=True)
        
        return JsonResponse({
            'success': True, 
            'message': f'تم تحديد {updated_count} رسالة كمقروءة',
            'updated_count': updated_count
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'بيانات غير صحيحة'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

