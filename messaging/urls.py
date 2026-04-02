from django.urls import path
from . import views

app_name = 'messages'

urlpatterns = [
    # Conversations
    path('', views.conversations_list, name='conversations_list'),
    path('inbox/', views.inbox, name='inbox'),
    path('conversation/<int:conversation_id>/', views.conversation_detail, name='conversation_detail'),
    path('start/<int:user_id>/', views.start_conversation, name='start_conversation'),
    path('conversation/<int:conversation_id>/block/', views.block_conversation, name='block_conversation'),
    path('conversation/<int:conversation_id>/typing/', views.typing_indicator, name='typing_indicator'),
    
    # Notifications
    path('notifications/', views.notifications, name='notifications'),
    path('notification/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
]
