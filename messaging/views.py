from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Q, Count
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import Message, Notification, Conversation, MessageAttachment, TypingIndicator
from .forms import MessageForm, ConversationForm

User = get_user_model()

@login_required
def conversations_list(request):
    """List all conversations for the user"""
    if request.user.account_status == 'blocked':
        messages.error(request, 'Your account is blocked. Please submit an appeal from your profile page to regain messaging access.')
        return redirect('accounts:profile')

    # Check if farmer is verified
    if request.user.role == 'farmer' and request.user.farmer_verification_status != 'verified':
        messages.error(request, 'Only verified farmers can access messaging. Complete verification to use this feature.')
        return redirect('accounts:dashboard')
    
    conversations = Conversation.objects.with_unread_count(request.user).order_by('-updated_at')
    
    context = {
        'conversations': conversations
    }
    return render(request, 'messages/conversations_list.html', context)


@login_required
def conversation_detail(request, conversation_id):
    """View a specific conversation"""
    if request.user.account_status == 'blocked':
        messages.error(request, 'Your account is blocked. Please submit an appeal from your profile page to regain messaging access.')
        return redirect('accounts:profile')

    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    # Check authorization
    if request.user not in conversation.participants.all():
        messages.error(request, 'You do not have access to this conversation.')
        return redirect('messages:conversations_list')
    
    # Build conversation list with unread counters for sidebar display
    conversations = Conversation.objects.with_unread_count(request.user).order_by('-updated_at')
    
    # Mark all unread messages in this conversation as read
    unread_messages = conversation.messages.filter(is_read=False).exclude(sender=request.user)
    for msg in unread_messages:
        msg.mark_as_read()
    
    if request.method == 'POST':
        if request.user.role == 'farmer' and request.user.farmer_verification_status != 'verified':
            messages.error(request, 'Your farmer account is not verified. Messaging is limited until verification is complete.')
            return redirect('accounts:dashboard')

        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = request.user
            message.save()
            
            # Create notification for other participant
            other_user = conversation.get_other_user(request.user)
            if other_user:
                Notification.objects.create(
                    user=other_user,
                    notification_type='message',
                    title='New Message',
                    message=f'{request.user.username} sent you a message',
                    related_object_id=message.id,
                    related_object_type='Message'
                )
            
            return redirect('messages:conversation_detail', conversation_id=conversation.id)
    else:
        form = MessageForm()
    
    messages_list = conversation.messages.order_by('timestamp')
    context = {
        'conversation': conversation,
        'messages': messages_list,
        'form': form,
        'other_user': conversation.get_other_user(request.user),
        'conversations': conversations,
    }
    
    return render(request, 'messages/conversation_detail.html', context)


@login_required
def start_conversation(request, user_id):
    """Start a new conversation with a user"""
    if request.user.account_status == 'blocked':
        messages.error(request, 'Your account is blocked. Please submit an appeal from your profile page to regain messaging access.')
        return redirect('accounts:profile')

    other_user = get_object_or_404(User, id=user_id)
    
    if other_user == request.user:
        messages.error(request, 'You cannot chat with yourself.')
        return redirect('messages:conversations_list')

    if request.user.role == 'farmer' and request.user.farmer_verification_status != 'verified':
        messages.error(request, 'Your farmer account is not verified. Messaging is limited until verification is complete.')
        return redirect('accounts:dashboard')
    
    # Check if conversation already exists
    existing_conversation = (
        Conversation.objects
        .filter(participants=request.user)
        .filter(participants=other_user)
        .first()
    )
    
    if existing_conversation:
        return redirect('messages:conversation_detail', conversation_id=existing_conversation.id)
    
    # Create new conversation
    conversation = Conversation.objects.create()
    conversation.participants.add(request.user, other_user)
    
    return redirect('messages:conversation_detail', conversation_id=conversation.id)


@login_required
def inbox(request):
    """Legacy inbox view - redirects to conversations list"""
    return redirect('messages:conversations_list')


@login_required
def notifications(request):
    """View user notifications"""
    user_notifications = request.user.notifications.order_by('-created_at')
    
    # Mark viewed notifications as read
    if request.method == 'POST':
        notification_id = request.POST.get('notification_id')
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        notification.mark_as_read()
        return redirect('messages:notifications')
    
    context = {
        'notifications': user_notifications,
        'unread_count': user_notifications.filter(is_read=False).count(),
    }
    
    return render(request, 'messages/notifications.html', context)


@login_required
@require_POST
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.mark_as_read()
    messages.success(request, 'Notification marked as read.')
    return redirect(request.META.get('HTTP_REFERER', 'messages:notifications'))


@login_required
def typing_indicator(request, conversation_id):
    """Update typing indicator for a conversation (WebSocket would be better)"""
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    if request.user not in conversation.participants.all():
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    # Remove old typing indicators
    TypingIndicator.objects.filter(
        conversation=conversation,
        user=request.user,
        started_at__lt=timezone.now() - timezone.timedelta(seconds=3)
    ).delete()
    
    # Create/update typing indicator
    TypingIndicator.objects.update_or_create(
        conversation=conversation,
        user=request.user,
        defaults={'started_at': timezone.now()}
    )
    
    # Get other typing users
    typing_users = TypingIndicator.objects.filter(
        conversation=conversation
    ).exclude(user=request.user).values_list('user__username', flat=True)
    
    return JsonResponse({'typing_users': list(typing_users)})


@login_required
def block_conversation(request, conversation_id):
    """Block a conversation (prevent further messages)"""
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    if request.user not in conversation.participants.all():
        messages.error(request, 'Unauthorized action.')
        return redirect('messages:conversations_list')
    
    conversation.is_blocked = True
    conversation.save()
    
    messages.success(request, 'Conversation has been blocked.')
    return redirect('messages:conversations_list')
