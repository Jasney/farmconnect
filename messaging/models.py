from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Count, Q

User = get_user_model()

class ConversationManager(models.Manager):
    """Custom manager for Conversation model"""
    
    def with_unread_count(self, user):
        """Get conversations with unread message count for a specific user"""
        return self.filter(participants=user).annotate(
            unread_count=Count(
                'messages',
                filter=Q(messages__is_read=False) & ~Q(messages__sender=user)
            )
        )

class Conversation(models.Model):
    """Thread of messages between two users"""
    participants = models.ManyToManyField(User, related_name='conversations')
    subject = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_blocked = models.BooleanField(default=False)
    
    objects = ConversationManager()

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f"Conversation: {', '.join([u.username for u in self.participants.all()])}"
    
    def get_other_user(self, user):
        """Get the other participant in the conversation"""
        return self.participants.exclude(id=user.id).first()
    
    def get_unread_count(self, user):
        """Get unread message count for a specific user"""
        return self.messages.filter(is_read=False).exclude(sender=user).count()


class Message(models.Model):
    """Individual message in a conversation"""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Editing & moderation
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    is_flagged = models.BooleanField(default=False)
    flag_reason = models.CharField(max_length=200, blank=True)
    deleted_by_admin = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['conversation_id', 'timestamp']),
            models.Index(fields=['is_read']),
        ]

    def __str__(self):
        return f'{self.sender.username} to conversation {self.conversation.id}: {self.content[:50]}'
    
    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()


class MessageAttachment(models.Model):
    """File attachments for messages"""
    ATTACHMENT_TYPES = (
        ('image', 'Image'),
        ('document', 'Document'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('other', 'Other'),
    )
    
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='message_attachments/')
    file_type = models.CharField(max_length=20, choices=ATTACHMENT_TYPES)
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()  # In bytes
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # For images - thumbnail
    thumbnail = models.ImageField(upload_to='message_thumbnails/', null=True, blank=True)

    class Meta:
        ordering = ['uploaded_at']

    def __str__(self):
        return f"{self.file_name} in message {self.message.id}"


class TypingIndicator(models.Model):
    """Real-time typing indicator"""
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='typing_indicators')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    started_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('conversation', 'user')

    def __str__(self):
        return f"{self.user.username} typing in conversation {self.conversation.id}"


class Notification(models.Model):
    """User notifications for various system events"""
    NOTIFICATION_TYPES = (
        ('message', 'New Message'),
        ('review', 'New Review'),
        ('purchase', 'Purchase Request'),
        ('verification', 'Verification Status'),
        ('rating', 'Rating Update'),
        ('account', 'Account Action'),
        ('system', 'System Alert'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='system')
    title = models.CharField(max_length=200, default='System Notification')
    message = models.TextField()
    related_object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object_type = models.CharField(max_length=50, blank=True)  # Model name
    
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_id', 'is_read']),
        ]

    def __str__(self):
        return f'Notification for {self.user}: {self.title[:50]}'
    
    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()

