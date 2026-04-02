from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('farmer-rankings/', views.farmer_rankings, name='farmer_rankings'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('profile/', views.profile, name='profile'),
    path('admin/users/', views.user_management, name='user_management'),
    path('admin/listings/', views.listing_moderation, name='listing_moderation'),
    path('admin/activity/', views.activity_logs, name='activity_logs'),
    path('forgot-password/', auth_views.PasswordResetView.as_view(template_name='accounts/forgot_password.html'), name='forgot_password'),
    path('password-reset-done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), name='password_reset_done'),
    path('reset-password/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='accounts/reset_password.html'), name='reset_password'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), name='password_reset_complete'),
    path('farmer-verification/', views.farmer_verification, name='farmer_verification'),
    path('report-farmer/', views.report_farmer_list, name='report_farmer_list'),
    path('report-farmer/<int:farmer_id>/', views.report_farmer, name='report_farmer'),
]

