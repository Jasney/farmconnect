from django import forms
from .models import Message, MessageAttachment, Conversation


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Type your message...',
                'id': 'message-input'
            })
        }


class ConversationForm(forms.ModelForm):
    class Meta:
        model = Conversation
        fields = ['subject']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Conversation subject (optional)'
            })
        }


class MessageAttachmentForm(forms.ModelForm):
    class Meta:
        model = MessageAttachment
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.doc,.docx,.jpg,.jpeg,.png,.gif,.mp4,.webm'
            })
        }
