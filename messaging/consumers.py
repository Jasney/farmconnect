import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Conversation, Message, TypingIndicator
from django.utils import timezone

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Mark messages as read when user connects
        await self.mark_messages_read()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        # Remove typing indicator
        await self.remove_typing_indicator()
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'chat_message':
            await self.handle_chat_message(data)
        elif message_type == 'typing_start':
            await self.handle_typing_start()
        elif message_type == 'typing_stop':
            await self.handle_typing_stop()
    
    async def handle_chat_message(self, data):
        message_content = data['message']
        user = self.scope['user']
        
        if not user.is_authenticated:
            return
        
        # Save message to database
        message = await self.save_message(user, message_content)
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message_content,
                'user_id': user.id,
                'username': user.username,
                'timestamp': message.timestamp.isoformat(),
                'message_id': message.id,
            }
        )
    
    async def handle_typing_start(self):
        user = self.scope['user']
        if not user.is_authenticated:
            return
        
        await self.set_typing_indicator(user, True)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_indicator',
                'user_id': user.id,
                'username': user.username,
                'is_typing': True,
            }
        )
    
    async def handle_typing_stop(self):
        user = self.scope['user']
        if not user.is_authenticated:
            return
        
        await self.set_typing_indicator(user, False)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_indicator',
                'user_id': user.id,
                'username': user.username,
                'is_typing': False,
            }
        )
    
    # Receive message from room group
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'user_id': event['user_id'],
            'username': event['username'],
            'timestamp': event['timestamp'],
            'message_id': event['message_id'],
        }))
    
    async def typing_indicator(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'user_id': event['user_id'],
            'username': event['username'],
            'is_typing': event['is_typing'],
        }))
    
    @database_sync_to_async
    def save_message(self, user, content):
        conversation = Conversation.objects.get(id=self.conversation_id)
        message = Message.objects.create(
            conversation=conversation,
            sender=user,
            content=content,
        )
        return message
    
    @database_sync_to_async
    def mark_messages_read(self):
        user = self.scope['user']
        if user.is_authenticated:
            Message.objects.filter(
                conversation_id=self.conversation_id,
                is_read=False
            ).exclude(sender=user).update(is_read=True, read_at=timezone.now())
    
    @database_sync_to_async
    def set_typing_indicator(self, user, is_typing):
        conversation = Conversation.objects.get(id=self.conversation_id)
        if is_typing:
            TypingIndicator.objects.get_or_create(
                conversation=conversation,
                user=user,
                defaults={'started_at': timezone.now()}
            )
        else:
            TypingIndicator.objects.filter(
                conversation=conversation,
                user=user
            ).delete()
    
    @database_sync_to_async
    def remove_typing_indicator(self):
        user = self.scope['user']
        if user.is_authenticated:
            TypingIndicator.objects.filter(
                conversation_id=self.conversation_id,
                user=user
            ).delete()