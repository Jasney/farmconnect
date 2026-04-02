from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('dashboard/', views.admin_dashboard, name='dashboard'),
    path('users/', views.user_management, name='user_management'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/<int:user_id>/flag/', views.flag_user, name='flag_user'),
    path('users/<int:user_id>/suspend/', views.suspend_user, name='suspend_user'),
    path('reports/', views.user_reports, name='user_reports'),
    path('reports/<int:report_id>/', views.report_detail, name='report_detail'),
    path('verifications/', views.manage_verifications, name='manage_verifications'),
    path('verifications/<int:user_id>/approve/', views.approve_verification, name='approve_verification'),
    path('verifications/<int:user_id>/reject/', views.reject_verification, name='reject_verification'),
    path('logs/', views.activity_logs, name='activity_logs'),
    path('analytics/', views.platform_analytics, name='platform_analytics'),
    path('ai-monitoring/', views.ai_monitoring, name='ai_monitoring'),
    path('appeals/', views.account_appeals, name='account_appeals'),
    path('appeals/<int:appeal_id>/', views.appeal_detail, name='appeal_detail'),
]
