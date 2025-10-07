from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from messaging.models import Message, Conversation
from products.models import Product

User = get_user_model()

class Command(BaseCommand):
    help = 'إصلاح المحادثات الموجودة وربطها بالرسائل'

    def handle(self, *args, **options):
        # إنشاء محادثات للرسائل التي لا تحتوي على محادثة
        messages_without_conversation = Message.objects.filter(conversation__isnull=True)
        
        self.stdout.write(
            self.style.WARNING(
                'العثور على {} رسالة بدون محادثة'.format(messages_without_conversation.count())
            )
        )
        
        conversations_created = 0
        
        for message in messages_without_conversation:
            # البحث عن محادثة موجودة بين نفس المستخدمين ونفس المنتج
            existing_conversation = Conversation.objects.filter(
                participants=message.sender,
                product=message.product
            ).filter(participants=message.receiver).first()
            
            if existing_conversation:
                # ربط الرسالة بالمحادثة الموجودة
                message.conversation = existing_conversation
                message.save()
            else:
                # إنشاء محادثة جديدة
                conversation = Conversation.objects.create(product=message.product)
                conversation.participants.add(message.sender, message.receiver)
                
                # ربط الرسالة بالمحادثة الجديدة
                message.conversation = conversation
                message.save()
                
                conversations_created += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                'تم إنشاء {} محادثة جديدة'.format(conversations_created)
            )
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                'تم إصلاح جميع الرسائل بنجاح!'
            )
        ) 