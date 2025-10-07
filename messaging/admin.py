from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Message, Conversation
from django.utils import timezone
from django.db import models

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'sender_info', 'receiver_info', 'product_link', 
        'content_preview', 'timestamp', 'is_read_status'
    ]
    list_filter = [
        'timestamp', 'is_read', 'product__category', 
        'sender__is_seller', 'receiver__is_seller'
    ]
    search_fields = [
        'sender__username', 'sender__first_name', 'sender__last_name',
        'receiver__username', 'receiver__first_name', 'receiver__last_name', 
        'content', 'product__title'
    ]
    readonly_fields = ['timestamp', 'conversation_link']
    ordering = ['-timestamp']
    date_hierarchy = 'timestamp'
    list_per_page = 25
    
    fieldsets = (
        ('معلومات الرسالة', {
            'fields': ('sender', 'receiver', 'content', 'timestamp')
        }),
        ('معلومات المنتج', {
            'fields': ('product', 'conversation_link')
        }),
        ('حالة الرسالة', {
            'fields': ('is_read',)
        }),
    )
    
    def sender_info(self, obj):
        """عرض معلومات المرسل"""
        if obj.sender:
            name = obj.sender.get_full_name() or obj.sender.username
            seller_badge = ' 🏪' if obj.sender.is_seller else ' 👤'
            return format_html(
                '<strong>{}</strong>{}<br><small>{}</small>',
                name, seller_badge, obj.sender.username
            )
        return '-'
    sender_info.short_description = 'المرسل'
    
    def receiver_info(self, obj):
        """عرض معلومات المستقبل"""
        if obj.receiver:
            name = obj.receiver.get_full_name() or obj.receiver.username
            seller_badge = ' 🏪' if obj.receiver.is_seller else ' 👤'
            return format_html(
                '<strong>{}</strong>{}<br><small>{}</small>',
                name, seller_badge, obj.receiver.username
            )
        return '-'
    receiver_info.short_description = 'المستقبل'
    
    def product_link(self, obj):
        """رابط للمنتج"""
        if obj.product:
            return format_html(
                '<a href="{}" target="_blank">{}</a><br><small>السعر: {} ر.س</small>',
                reverse('admin:products_product_change', args=[obj.product.pk]),
                obj.product.title[:30] + '...' if len(obj.product.title) > 30 else obj.product.title,
                obj.product.price
            )
        return '-'
    product_link.short_description = 'المنتج'
    
    def content_preview(self, obj):
        """معاينة المحتوى"""
        if len(obj.content) > 50:
            return obj.content[:50] + '...'
        return obj.content
    content_preview.short_description = 'المحتوى'
    
    def is_read_status(self, obj):
        """حالة القراءة مع أيقونة"""
        if obj.is_read:
            return format_html('<span style="color: green;">✅ مقروءة</span>')
        else:
            return format_html('<span style="color: red;">❌ غير مقروءة</span>')
    is_read_status.short_description = 'حالة القراءة'
    
    def conversation_link(self, obj):
        """رابط للمحادثة"""
        if obj.conversation:
            return format_html(
                '<a href="{}" target="_blank">عرض المحادثة</a>',
                reverse('admin:messaging_conversation_change', args=[obj.conversation.pk])
            )
        return 'لا توجد محادثة'
    conversation_link.short_description = 'المحادثة'
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        """تحديد الرسائل كمقروءة"""
        updated = queryset.update(is_read=True)
        self.message_user(request, f'تم تحديد {updated} رسالة كمقروءة.')
    mark_as_read.short_description = 'تحديد كمقروءة'
    
    def mark_as_unread(self, request, queryset):
        """تحديد الرسائل كغير مقروءة"""
        updated = queryset.update(is_read=False)
        self.message_user(request, f'تم تحديد {updated} رسالة كغير مقروءة.')
    mark_as_unread.short_description = 'تحديد كغير مقروءة'

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = [
        'conversation_id', 'product_preview', 'participants_summary', 
        'messages_stats', 'conversation_status', 'last_activity', 'created_at'
    ]
    list_filter = [
        'created_at', 'updated_at', 'product__category',
        'product__status', 'product__seller__is_seller'
    ]
    search_fields = [
        'product__title', 'participants__username', 
        'participants__first_name', 'participants__last_name',
        'messages__content'
    ]
    filter_horizontal = ['participants']
    readonly_fields = ['created_at', 'updated_at', 'conversation_analysis', 'all_messages_display', 'product_management']
    ordering = ['-updated_at']
    date_hierarchy = 'created_at'
    list_per_page = 20
    
    fieldsets = (
        ('معلومات المحادثة الأساسية', {
            'fields': ('product', 'participants', 'created_at', 'updated_at'),
            'classes': ('wide',)
        }),
        ('إدارة المنتج', {
            'fields': ('product_management',),
            'classes': ('wide',),
            'description': 'يمكنك تغيير حالة المنتج من هنا'
        }),
        ('جميع الرسائل', {
            'fields': ('all_messages_display',),
            'classes': ('wide',)
        }),
        ('تحليل المحادثة', {
            'fields': ('conversation_analysis',),
            'classes': ('collapse', 'wide')
        }),
    )
    
    def conversation_id(self, obj):
        """معرف المحادثة مع رابط"""
        return format_html(
            '<strong>#{}</strong><br>'
            '<small style="color: #6c757d;">محادثة</small>',
            obj.id
        )
    conversation_id.short_description = 'المعرف'
    
    def product_preview(self, obj):
        """معاينة المنتج مع صورة وتفاصيل"""
        if obj.product:
            # محاولة الحصول على أول صورة
            first_image = obj.product.images.first()
            image_html = ''
            if first_image and first_image.image:
                image_html = f'<img src="{first_image.image.url}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 8px; margin-right: 10px; float: right;">'
            
            # تحديد حالة المنتج وتنسيقها
            status_colors = {
                'active': '#28a745',
                'pending_approval': '#ffc107', 
                'sold': '#dc3545',
                'inactive': '#6c757d'
            }
            status_labels = {
                'active': 'نشط',
                'pending_approval': 'في الانتظار',
                'sold': 'مباع', 
                'inactive': 'غير نشط'
            }
            
            status_color = status_colors.get(obj.product.status, '#6c757d')
            status_label = status_labels.get(obj.product.status, obj.product.status)
            
            return format_html(
                '<div style="display: flex; align-items: center; min-height: 60px;">'
                '<div style="flex: 1;">'
                '<a href="{}" target="_blank"><strong>{}</strong></a><br>'
                '<small style="color: #28a745; font-weight: bold;">{} ر.س</small><br>'
                '<small style="color: #6c757d;">البائع: {}</small><br>'
                '<span style="background: {}; color: white; padding: 2px 6px; border-radius: 10px; font-size: 10px;">{}</span>'
                '</div>'
                '{}'
                '</div>',
                reverse('admin:products_product_change', args=[obj.product.pk]),
                obj.product.title[:35] + '...' if len(obj.product.title) > 35 else obj.product.title,
                obj.product.price,
                obj.product.seller.get_full_name() or obj.product.seller.username,
                status_color,
                status_label,
                image_html
            )
        return '<span style="color: #dc3545;">لا يوجد منتج</span>'
    product_preview.short_description = 'المنتج'
    
    def participants_summary(self, obj):
        """ملخص المشاركين مع أيقونات وألوان"""
        participants = obj.participants.all()
        if not participants:
            return '<span style="color: #dc3545;">لا يوجد مشاركين</span>'
        
        html_parts = []
        for i, participant in enumerate(participants):
            name = participant.get_full_name() or participant.username
            
            # تحديد نوع المشارك
            if obj.product and participant == obj.product.seller:
                role = 'البائع'
                icon = '🏪'
                color = '#007bff'
            else:
                role = 'المشتري'
                icon = '👤'
                color = '#28a745'
            
            # حساب عدد رسائل هذا المشارك
            messages_count = obj.messages.filter(sender=participant).count()
            
            html_parts.append(
                f'<div style="margin-bottom: 8px; padding: 8px; background: {color}15; border-left: 3px solid {color}; border-radius: 4px;">'
                f'<strong>{icon} {name}</strong><br>'
                f'<small style="color: {color}; font-weight: bold;">{role}</small><br>'
                f'<small style="color: #6c757d;">{messages_count} رسالة</small>'
                f'</div>'
            )
        
        return format_html(''.join(html_parts))
    participants_summary.short_description = 'المشاركين'
    
    def messages_stats(self, obj):
        """إحصائيات الرسائل مع رسم بياني بسيط"""
        total_messages = obj.messages.count()
        unread_messages = obj.messages.filter(is_read=False).count()
        
        if total_messages == 0:
            return format_html('<span style="color: #6c757d;">لا توجد رسائل</span>')
        
        # حساب النسب
        read_percentage = ((total_messages - unread_messages) / total_messages) * 100
        unread_percentage = (unread_messages / total_messages) * 100
        
        return format_html(
            '<div style="text-align: center;">'
            '<div style="font-size: 18px; font-weight: bold; color: #007bff; margin-bottom: 5px;">{}</div>'
            '<div style="font-size: 12px; color: #6c757d; margin-bottom: 8px;">إجمالي الرسائل</div>'
            
            '<div style="background: #e9ecef; border-radius: 10px; height: 8px; margin-bottom: 5px; overflow: hidden;">'
            '<div style="background: #28a745; height: 100%; width: {}%; float: left;"></div>'
            '<div style="background: #dc3545; height: 100%; width: {}%;"></div>'
            '</div>'
            
            '<div style="display: flex; justify-content: space-between; font-size: 10px;">'
            '<span style="color: #28a745;">✅ {} مقروءة</span>'
            '<span style="color: #dc3545;">❌ {} غير مقروءة</span>'
            '</div>'
            '</div>',
            total_messages,
            read_percentage,
            unread_percentage,
            total_messages - unread_messages,
            unread_messages
        )
    messages_stats.short_description = 'إحصائيات الرسائل'
    
    def conversation_status(self, obj):
        """حالة المحادثة مع مؤشرات بصرية"""
        total_messages = obj.messages.count()
        last_message = obj.messages.first()
        
        if total_messages == 0:
            status = 'فارغة'
            color = '#6c757d'
            icon = '📭'
        elif last_message and not last_message.is_read:
            status = 'جديدة'
            color = '#dc3545'
            icon = '🔴'
        elif last_message and (timezone.now() - last_message.timestamp).days < 1:
            status = 'نشطة'
            color = '#28a745'
            icon = '🟢'
        elif last_message and (timezone.now() - last_message.timestamp).days < 7:
            status = 'هادئة'
            color = '#ffc107'
            icon = '🟡'
        else:
            status = 'قديمة'
            color = '#6c757d'
            icon = '⚫'
        
        return format_html(
            '<div style="text-align: center;">'
            '<div style="font-size: 20px; margin-bottom: 5px;">{}</div>'
            '<span style="background: {}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>'
            '</div>',
            icon, color, status
        )
    conversation_status.short_description = 'الحالة'
    
    def last_activity(self, obj):
        """آخر نشاط مع تفاصيل"""
        last_message = obj.messages.first()
        if last_message:
            time_diff = timezone.now() - last_message.timestamp
            
            if time_diff.days > 0:
                time_str = f'{time_diff.days} يوم'
            elif time_diff.seconds > 3600:
                time_str = f'{time_diff.seconds // 3600} ساعة'
            elif time_diff.seconds > 60:
                time_str = f'{time_diff.seconds // 60} دقيقة'
            else:
                time_str = 'الآن'
            
            sender_name = last_message.sender.get_full_name() or last_message.sender.username
            
            return format_html(
                '<div style="text-align: center;">'
                '<div style="font-weight: bold; color: #007bff; margin-bottom: 3px;">منذ {}</div>'
                '<div style="font-size: 11px; color: #6c757d; margin-bottom: 5px;">بواسطة: {}</div>'
                '<div style="background: #f8f9fa; padding: 5px; border-radius: 4px; font-size: 10px; max-width: 150px; margin: 0 auto;">'
                '"{}"'
                '</div>'
                '</div>',
                time_str,
                sender_name,
                last_message.content[:30] + '...' if len(last_message.content) > 30 else last_message.content
            )
        
        return format_html('<span style="color: #6c757d;">لا توجد رسائل</span>')
    last_activity.short_description = 'آخر نشاط'
    
    def product_management(self, obj):
        """إدارة المنتج - تغيير الحالة"""
        if not obj.product:
            return '<span style="color: #dc3545;">لا يوجد منتج للإدارة</span>'
        
        product = obj.product
        
        # تعريف ألوان وتسميات الحالات
        status_colors = {
            'active': '#28a745',
            'pending_approval': '#ffc107', 
            'sold': '#dc3545',
            'inactive': '#6c757d'
        }
        status_labels = {
            'active': 'نشط',
            'pending_approval': 'في الانتظار',
            'sold': 'مباع', 
            'inactive': 'غير نشط'
        }
        
        # أزرار تغيير الحالة
        status_buttons = {
            'active': ('تفعيل المنتج', '#28a745', '🟢'),
            'pending_approval': ('في انتظار الموافقة', '#ffc107', '🟡'),
            'sold': ('تم البيع', '#dc3545', '🔴'),
            'inactive': ('إلغاء تفعيل', '#6c757d', '⚫')
        }
        
        html_content = f'''
        <div style="background: #f8f9fa; padding: 20px; border-radius: 12px; margin: 15px 0;">
            <h3 style="color: #495057; margin-bottom: 20px; text-align: center;">🛠️ إدارة المنتج</h3>
            
            <div style="background: white; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                <div style="display: flex; align-items: center; margin-bottom: 15px;">
        '''
        
        # عرض صورة المنتج إذا كانت موجودة
        first_image = product.images.first()
        if first_image and first_image.image:
            html_content += f'''
                    <img src="{first_image.image.url}" style="width: 80px; height: 80px; object-fit: cover; border-radius: 8px; margin-left: 15px;">
            '''
        
        html_content += f'''
                    <div style="flex: 1;">
                        <h4 style="margin: 0 0 10px 0; color: #495057;">
                            <a href="{reverse('admin:products_product_change', args=[product.pk])}" target="_blank" style="text-decoration: none;">
                                {product.title}
                            </a>
                        </h4>
                        <div style="margin-bottom: 8px;">
                            <strong>السعر:</strong> 
                            <span style="color: #28a745; font-weight: bold; font-size: 16px;">{product.price} ر.س</span>
                        </div>
                        <div style="margin-bottom: 8px;">
                            <strong>البائع:</strong> 
                            <span style="color: #007bff;">{product.seller.get_full_name() or product.seller.username}</span>
                        </div>
                        <div style="margin-bottom: 8px;">
                            <strong>الفئة:</strong> 
                            <span style="color: #6c757d;">{product.category.name}</span>
                        </div>
                        <div>
                            <strong>الحالة الحالية:</strong> 
                            <span style="background: {status_colors.get(product.status, '#6c757d')}; color: white; padding: 4px 8px; border-radius: 12px; font-size: 12px;">
                                {status_labels.get(product.status, product.status)}
                            </span>
                        </div>
                    </div>
                </div>
                
                <div style="border-top: 1px solid #e9ecef; padding-top: 15px;">
                    <h5 style="color: #6c757d; margin-bottom: 15px;">تغيير حالة المنتج:</h5>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px;">
        '''
        
        # إنشاء أزرار تغيير الحالة
        for status, (label, color, icon) in status_buttons.items():
            disabled = 'disabled' if product.status == status else ''
            opacity = 'opacity: 0.5;' if product.status == status else ''
            
            html_content += f'''
                        <button type="button" 
                                onclick="changeProductStatus('{product.pk}', '{status}', '{obj.pk}')"
                                style="background: {color}; color: white; border: none; padding: 10px 15px; border-radius: 8px; cursor: pointer; font-size: 12px; {opacity}"
                                {disabled}>
                            {icon} {label}
                        </button>
            '''
        
        html_content += '''
                    </div>
                    <div id="status-change-result" style="margin-top: 15px; padding: 10px; border-radius: 4px; display: none;"></div>
                </div>
            </div>
        </div>
        
        <script>
        function changeProductStatus(productId, newStatus, conversationId) {
            if (!confirm('هل أنت متأكد من تغيير حالة المنتج؟')) {
                return;
            }
            
            const resultDiv = document.getElementById('status-change-result');
            resultDiv.style.display = 'block';
            resultDiv.innerHTML = '<div style="color: #007bff;">جاري تغيير الحالة...</div>';
            
            fetch('/admin/products/product/' + productId + '/change/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: 'status=' + newStatus + '&_save=Save'
            })
            .then(response => {
                if (response.ok) {
                    resultDiv.innerHTML = '<div style="color: #28a745; background: #d4edda; padding: 8px; border-radius: 4px;">✅ تم تغيير حالة المنتج بنجاح!</div>';
                    setTimeout(() => {
                        location.reload();
                    }, 1500);
                } else {
                    resultDiv.innerHTML = '<div style="color: #dc3545; background: #f8d7da; padding: 8px; border-radius: 4px;">❌ حدث خطأ في تغيير الحالة</div>';
                }
            })
            .catch(error => {
                resultDiv.innerHTML = '<div style="color: #dc3545; background: #f8d7da; padding: 8px; border-radius: 4px;">❌ حدث خطأ في الاتصال</div>';
            });
        }
        </script>
        '''
        
        return mark_safe(html_content)
    product_management.short_description = 'إدارة المنتج'
    
    def all_messages_display(self, obj):
        """عرض جميع الرسائل في المحادثة"""
        messages = obj.messages.all()
        
        if not messages:
            return '<div style="text-align: center; color: #6c757d; padding: 40px; background: #f8f9fa; border-radius: 8px;">📭 لا توجد رسائل في هذه المحادثة</div>'
        
        html_content = f'''
        <div style="background: #f8f9fa; padding: 20px; border-radius: 12px; margin: 15px 0;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h3 style="color: #495057; margin: 0;">💬 جميع الرسائل ({messages.count()})</h3>
                <div style="display: flex; gap: 10px;">
                    <button onclick="markAllAsRead({obj.pk})" style="background: #28a745; color: white; border: none; padding: 8px 15px; border-radius: 6px; cursor: pointer; font-size: 12px;">
                        ✅ تحديد الكل كمقروء
                    </button>
                    <button onclick="toggleMessageDetails()" style="background: #007bff; color: white; border: none; padding: 8px 15px; border-radius: 6px; cursor: pointer; font-size: 12px;">
                        📋 إظهار/إخفاء التفاصيل
                    </button>
                </div>
            </div>
            
            <div style="max-height: 600px; overflow-y: auto; background: white; border-radius: 8px; padding: 15px;">
        '''
        
        for i, message in enumerate(messages):
            sender_name = message.sender.get_full_name() or message.sender.username
            
            # تحديد جانب الرسالة ولونها وأيقونة المرسل
            if obj.product and message.sender == obj.product.seller:
                align = 'right'
                bg_color = '#007bff'
                text_color = 'white'
                role = 'البائع'
                role_icon = '🏪'
                border_side = 'border-right'
            else:
                align = 'left'
                bg_color = '#28a745'
                text_color = 'white'
                role = 'المشتري'
                role_icon = '👤'
                border_side = 'border-left'
            
            # أيقونة حالة القراءة
            read_icon = '✅' if message.is_read else '❌'
            read_status = 'مقروءة' if message.is_read else 'غير مقروءة'
            
            # تنسيق الوقت
            time_diff = timezone.now() - message.timestamp
            if time_diff.days > 0:
                time_str = f'{time_diff.days} يوم'
            elif time_diff.seconds > 3600:
                time_str = f'{time_diff.seconds // 3600} ساعة'
            elif time_diff.seconds > 60:
                time_str = f'{time_diff.seconds // 60} دقيقة'
            else:
                time_str = 'الآن'
            
            html_content += f'''
                <div style="margin-bottom: 20px; text-align: {align};" class="message-item">
                    <div style="display: inline-block; max-width: 75%; background: {bg_color}; color: {text_color}; padding: 15px 18px; border-radius: 18px; position: relative; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                        <!-- Header الرسالة -->
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; font-size: 11px; opacity: 0.9; border-bottom: 1px solid rgba(255,255,255,0.2); padding-bottom: 6px;">
                            <div>
                                <strong>{role_icon} {sender_name}</strong>
                                <span style="margin-right: 8px; font-size: 10px;">({role})</span>
                            </div>
                            <div style="display: flex; align-items: center; gap: 8px;">
                                <span>{read_icon}</span>
                                <span>#{message.pk}</span>
                            </div>
                        </div>
                        
                        <!-- محتوى الرسالة -->
                        <div style="margin-bottom: 10px; line-height: 1.5; font-size: 14px;">
                            {message.content}
                        </div>
                        
                        <!-- Footer الرسالة -->
                        <div style="display: flex; justify-content: space-between; align-items: center; font-size: 10px; opacity: 0.8;">
                            <span>{message.timestamp.strftime("%Y-%m-%d %H:%M")}</span>
                            <span>منذ {time_str}</span>
                        </div>
                        
                        <!-- تفاصيل إضافية (مخفية افتراضياً) -->
                        <div class="message-details" style="display: none; margin-top: 10px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.2); font-size: 10px; opacity: 0.8;">
                            <div style="margin-bottom: 4px;">
                                <strong>الحالة:</strong> {read_status}
                            </div>
                            <div style="margin-bottom: 4px;">
                                <strong>المستقبل:</strong> {message.receiver.get_full_name() or message.receiver.username if message.receiver else 'غير محدد'}
                            </div>
                            <div style="margin-bottom: 4px;">
                                <strong>المنتج:</strong> {message.product.title[:30] + '...' if message.product and len(message.product.title) > 30 else message.product.title if message.product else 'غير محدد'}
                            </div>
                            <div>
                                <strong>طول الرسالة:</strong> {len(message.content)} حرف
                            </div>
                        </div>
                    </div>
                </div>
            '''
        
        html_content += '''
            </div>
        </div>
        
        <script>
        function markAllAsRead(conversationId) {
            if (!confirm('هل تريد تحديد جميع الرسائل كمقروءة؟')) {
                return;
            }
            
            fetch('/admin/mark-messages-read/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({conversation_id: conversationId})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('✅ تم تحديد جميع الرسائل كمقروءة!');
                    location.reload();
                } else {
                    alert('❌ حدث خطأ في العملية');
                }
            })
            .catch(error => {
                alert('❌ حدث خطأ في الاتصال');
            });
        }
        
        function toggleMessageDetails() {
            const details = document.querySelectorAll('.message-details');
            details.forEach(detail => {
                if (detail.style.display === 'none') {
                    detail.style.display = 'block';
                } else {
                    detail.style.display = 'none';
                }
            });
        }
        </script>
        '''
        
        return mark_safe(html_content)
    all_messages_display.short_description = 'جميع الرسائل'
    
    def conversation_analysis(self, obj):
        """تحليل شامل للمحادثة"""
        if not obj.pk:
            return 'احفظ المحادثة أولاً لعرض التحليل'
        
        # إحصائيات المشاركين
        participants = obj.participants.all()
        messages_by_participant = {}
        
        for participant in participants:
            messages_count = obj.messages.filter(sender=participant).count()
            messages_by_participant[participant] = messages_count
        
        # إحصائيات عامة
        total_messages = obj.messages.count()
        avg_message_length = obj.messages.aggregate(
            avg_length=models.Avg(models.Length('content'))
        )['avg_length'] or 0
        
        # إحصائيات زمنية
        conversation_duration = obj.updated_at - obj.created_at
        
        html_content = f'''
        <div style="background: #f8f9fa; padding: 20px; border-radius: 12px; margin: 15px 0;">
            <h3 style="color: #495057; margin-bottom: 20px; text-align: center;">📊 تحليل شامل للمحادثة</h3>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                <div style="background: white; padding: 15px; border-radius: 8px; text-align: center; border-left: 4px solid #007bff;">
                    <h4 style="color: #007bff; margin: 0 0 10px 0;">إجمالي الرسائل</h4>
                    <div style="font-size: 24px; font-weight: bold; color: #495057;">{total_messages}</div>
                </div>
                
                <div style="background: white; padding: 15px; border-radius: 8px; text-align: center; border-left: 4px solid #28a745;">
                    <h4 style="color: #28a745; margin: 0 0 10px 0;">متوسط طول الرسالة</h4>
                    <div style="font-size: 24px; font-weight: bold; color: #495057;">{avg_message_length:.0f} حرف</div>
                </div>
                
                <div style="background: white; padding: 15px; border-radius: 8px; text-align: center; border-left: 4px solid #ffc107;">
                    <h4 style="color: #ffc107; margin: 0 0 10px 0;">مدة المحادثة</h4>
                    <div style="font-size: 24px; font-weight: bold; color: #495057;">{conversation_duration.days} يوم</div>
                </div>
            </div>
            
            <div style="background: white; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                <h4 style="color: #6c757d; margin-bottom: 15px;">📈 توزيع الرسائل حسب المشارك</h4>
        '''
        
        for participant, count in messages_by_participant.items():
            percentage = (count / total_messages * 100) if total_messages > 0 else 0
            name = participant.get_full_name() or participant.username
            
            # تحديد لون الشريط
            if obj.product and participant == obj.product.seller:
                bar_color = '#007bff'
                role = 'البائع'
            else:
                bar_color = '#28a745'
                role = 'المشتري'
            
            html_content += f'''
                <div style="margin-bottom: 15px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 5px;">
                        <span style="font-weight: bold;">{name} ({role})</span>
                        <span style="color: #6c757d;">{count} رسالة ({percentage:.1f}%)</span>
                    </div>
                    <div style="background: #e9ecef; border-radius: 10px; height: 12px; overflow: hidden;">
                        <div style="background: {bar_color}; height: 100%; width: {percentage}%; transition: width 0.3s ease;"></div>
                    </div>
                </div>
            '''
        
        html_content += '''
            </div>
            
            <div style="background: white; padding: 15px; border-radius: 8px;">
                <h4 style="color: #6c757d; margin-bottom: 10px;">ℹ️ معلومات إضافية</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
        '''
        
        # معلومات إضافية
        first_message = obj.messages.last()
        last_message = obj.messages.first()
        
        html_content += f'''
                    <div>
                        <strong>تاريخ بداية المحادثة:</strong><br>
                        <span style="color: #6c757d;">{obj.created_at.strftime("%Y-%m-%d %H:%M")}</span>
                    </div>
                    <div>
                        <strong>آخر تحديث:</strong><br>
                        <span style="color: #6c757d;">{obj.updated_at.strftime("%Y-%m-%d %H:%M")}</span>
                    </div>
        '''
        
        if first_message:
            html_content += f'''
                    <div>
                        <strong>أول رسالة بواسطة:</strong><br>
                        <span style="color: #6c757d;">{first_message.sender.get_full_name() or first_message.sender.username}</span>
                    </div>
            '''
        
        if last_message:
            html_content += f'''
                    <div>
                        <strong>آخر رسالة بواسطة:</strong><br>
                        <span style="color: #6c757d;">{last_message.sender.get_full_name() or last_message.sender.username}</span>
                    </div>
            '''
        
        html_content += '''
                </div>
            </div>
        </div>
        '''
        
        return mark_safe(html_content)
    conversation_analysis.short_description = 'تحليل المحادثة'
