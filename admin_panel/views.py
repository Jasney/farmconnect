from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q, Count, Avg, Sum
from django.utils import timezone
from datetime import timedelta
from .models import (
    UserReport, AdminActionLog, AccountAppeal, FarmerActivityMetric,
    InactiveAccountFlag, SystemAuditLog, PlatformStats
)
from crops.models import Review, Crop, PurchaseRequest
from accounts.models import CustomUser, FarmerProfile

User = get_user_model()

def is_admin(user):
    """Check if user is an admin"""
    return user.is_staff or user.role == 'admin'

@login_required
def admin_dashboard(request):
    """Main admin dashboard"""
    if not is_admin(request.user):
        return redirect('home')
    
    context = {
        'total_users': User.objects.count(),
        'total_farmers': User.objects.filter(role='farmer').count(),
        'total_buyers': User.objects.filter(role='buyer').count(),
        'active_farmers': User.objects.filter(role='farmer', account_status='active').count(),
        'flagged_accounts': User.objects.filter(is_reported=True).count(),
        'suspended_accounts': User.objects.filter(account_status='suspended').count(),
        'pending_reports': UserReport.objects.filter(status='pending').count(),
        'pending_appeals': AccountAppeal.objects.filter(status='pending').count(),
        'pending_verifications': CustomUser.objects.filter(farmer_verification_status='pending').count(),
        'total_products': Crop.objects.filter(is_active=True).count(),
        'total_reviews': Review.objects.filter(is_approved=True).count(),
        'pending_reviews': Review.objects.filter(is_approved=False).count(),
        'total_transactions': PurchaseRequest.objects.filter(status='completed').count(),
    }
    
    # Top-rated farmers
    context['top_farmers'] = (
        CustomUser.objects
        .filter(role='farmer', farmer_profile__isnull=False)
        .order_by('-farmer_profile__rating_score')[:5]
    )
    
    # Recent activity
    context['recent_actions'] = AdminActionLog.objects.select_related('admin', 'target_user')[:10]
    context['recent_reports'] = UserReport.objects.select_related('reported_user', 'reporter')[:5]
    
    return render(request, 'admin/dashboard.html', context)


@login_required
def user_management(request):
    """Manage all users - view, flag, suspend, block"""
    if not is_admin(request.user):
        return redirect('home')
    
    users = User.objects.filter(role__in=['farmer', 'buyer']).order_by('-date_joined')
    
    # Filtering
    role = request.GET.get('role')
    status = request.GET.get('status')
    
    if role:
        users = users.filter(role=role)
    if status:
        users = users.filter(account_status=status)
    
    context = {
        'users': users,
        'role_filter': role,
        'status_filter': status,
    }
    
    return render(request, 'admin/user_management.html', context)


@login_required
def user_detail(request, user_id):
    """View detailed profile of a user"""
    if not is_admin(request.user):
        return redirect('home')
    
    user = get_object_or_404(User, id=user_id)
    
    context = {
        'profile_user': user,
        'reports_against': UserReport.objects.filter(reported_user=user),
        'actions_against': AdminActionLog.objects.filter(target_user=user),
    }
    
    if user.role == 'farmer':
        context['products'] = Crop.objects.filter(farmer=user)
        context['reviews'] = Review.objects.filter(farmer=user)
        context['analytics'] = FarmerActivityMetric.objects.filter(farmer=user).order_by('-date')[:30]
    
    return render(request, 'admin/user_detail.html', context)


@login_required
def flag_user(request, user_id):
    """Flag a user account for suspicious activity"""
    if not is_admin(request.user):
        return redirect('home')
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        new_status = request.POST.get('new_status', 'flagged')
        
        user.account_status = new_status
        user.is_reported = True
        user.save()
        
        # Log action
        AdminActionLog.objects.create(
            admin=request.user,
            action_type='user_flagged' if new_status == 'flagged' else f'user_{new_status}',
            target_user=user,
            description=f"User flagged by {request.user.username}",
            reason=reason
        )
        
        return redirect('admin:user_detail', user_id=user.id)
    
    return render(request, 'admin/flag_user.html', {'user': user})


@login_required
def suspend_user(request, user_id):
    """Suspend a user account temporarily"""
    if not is_admin(request.user):
        return redirect('home')
    
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        suspension_days = int(request.POST.get('suspension_days', 7))
        reason = request.POST.get('reason', '')
        
        user.account_status = 'suspended'
        user.suspension_reason = reason
        user.suspension_until = timezone.now() + timedelta(days=suspension_days)
        user.save()
        
        AdminActionLog.objects.create(
            admin=request.user,
            action_type='user_suspended',
            target_user=user,
            description=f"User suspended for {suspension_days} days",
            reason=reason
        )
        
        return redirect('admin:user_detail', user_id=user.id)
    
    return render(request, 'admin/suspend_user.html', {'user': user})


@login_required
def manage_verifications(request):
    """Manage farmer verification requests"""
    if not is_admin(request.user):
        return redirect('home')
    
    pending_farmers = CustomUser.objects.filter(
        role='farmer',
        farmer_verification_status__in=['pending', 'under_review']
    ).select_related('farmer_profile')
    
    context = {
        'pending_verifications': pending_farmers,
        'total_pending': pending_farmers.count(),
    }
    
    return render(request, 'admin/manage_verifications.html', context)


@login_required
def approve_verification(request, user_id):
    """Approve a farmer verification"""
    if not is_admin(request.user):
        return redirect('home')
    
    farmer = get_object_or_404(CustomUser, id=user_id, role='farmer')
    farmer.farmer_verification_status = 'verified'
    farmer.kyc_verified_date = timezone.now()
    farmer.save()
    
    AdminActionLog.objects.create(
        admin=request.user,
        action_type='verification_approved',
        target_user=farmer,
        description=f"Verification approved for {farmer.username}"
    )
    
    return redirect('admin_panel:manage_verifications')


@login_required
def reject_verification(request, user_id):
    """Reject a farmer verification"""
    if not is_admin(request.user):
        return redirect('home')
    
    farmer = get_object_or_404(CustomUser, id=user_id, role='farmer')
    farmer.farmer_verification_status = 'rejected'
    farmer.save()
    
    AdminActionLog.objects.create(
        admin=request.user,
        action_type='verification_rejected',
        target_user=farmer,
        description=f"Verification rejected for {farmer.username}"
    )
    
    return redirect('admin_panel:manage_verifications')


@login_required
def user_reports(request):
    """View all user reports"""
    if not is_admin(request.user):
        return redirect('home')
    
    reports = UserReport.objects.select_related('reported_user', 'reporter').order_by('-created_at')
    
    # Filtering
    status = request.GET.get('status')
    severity = request.GET.get('severity')
    
    if status:
        reports = reports.filter(status=status)
    if severity:
        reports = reports.filter(severity=severity)
    
    context = {
        'reports': reports,
        'status_filter': status,
        'severity_filter': severity,
        'total_pending': UserReport.objects.filter(status='pending').count(),
    }
    
    return render(request, 'admin/user_reports.html', context)


@login_required
def report_detail(request, report_id):
    """View and handle specific report"""
    if not is_admin(request.user):
        return redirect('home')
    
    report = get_object_or_404(UserReport, id=report_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        admin_notes = request.POST.get('admin_notes', '')
        
        if action == 'approve':
            report.status = 'resolved'
            # Take action on user
            user_action = request.POST.get('user_action')
            if user_action == 'suspend':
                report.reported_user.account_status = 'suspended'
                report.reported_user.suspension_reason = admin_notes
                report.reported_user.suspension_until = timezone.now() + timedelta(days=7)
                report.reported_user.save()
                AdminActionLog.objects.create(
                    admin=request.user,
                    action_type='user_suspended',
                    target_user=report.reported_user,
                    description=f"User suspended after report #{report.id}.",
                    reason=admin_notes,
                    related_report=report
                )
            elif user_action == 'block':
                report.reported_user.account_status = 'blocked'
                report.reported_user.save()
                AdminActionLog.objects.create(
                    admin=request.user,
                    action_type='user_blocked',
                    target_user=report.reported_user,
                    description=f"User blocked after report #{report.id}.",
                    reason=admin_notes,
                    related_report=report
                )
            elif user_action == 'warn':
                AdminActionLog.objects.create(
                    admin=request.user,
                    action_type='user_flagged',
                    target_user=report.reported_user,
                    description=f"User warned after report #{report.id}.",
                    reason=admin_notes,
                    related_report=report
                )
        elif action == 'dismiss':
            report.status = 'dismissed'

        report.admin_notes = admin_notes
        report.reviewed_by = request.user
        report.reviewed_at = timezone.now()
        report.save()
        
        return redirect('admin:user_reports')
    
    return render(request, 'admin/report_detail.html', {'report': report})


@login_required
def account_appeals(request):
    """View all farmer account appeals"""
    if not is_admin(request.user):
        return redirect('home')

    appeals = AccountAppeal.objects.select_related('farmer', 'reviewed_by').order_by('-created_at')
    return render(request, 'admin/account_appeals.html', {
        'appeals': appeals,
        'total_pending': AccountAppeal.objects.filter(status='pending').count(),
    })


@login_required
def appeal_detail(request, appeal_id):
    if not is_admin(request.user):
        return redirect('home')

    appeal = get_object_or_404(AccountAppeal, id=appeal_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        admin_notes = request.POST.get('admin_notes', '')

        if action == 'approve':
            appeal.status = 'approved'
            appeal.farmer.account_status = 'active'
            appeal.farmer.save()
            AdminActionLog.objects.create(
                admin=request.user,
                action_type='appeal_resolved',
                target_user=appeal.farmer,
                description=f"Farmer appeal approved: #{appeal.id}",
                reason=admin_notes,
                related_report=None
            )
        elif action == 'reject':
            appeal.status = 'rejected'

        appeal.admin_notes = admin_notes
        appeal.reviewed_by = request.user
        appeal.reviewed_at = timezone.now()
        appeal.save()

        return redirect('admin_panel:account_appeals')

    return render(request, 'admin/appeal_detail.html', {'appeal': appeal})


@login_required
def manage_verifications(request):
    """Manage farmer verification documents"""
    if not is_admin(request.user):
        return redirect('home')
    
    from accounts.models import VerificationDocument
    
    verifications = VerificationDocument.objects.select_related('farmer').filter(status='pending')
    
    context = {
        'verifications': verifications,
        'total_pending': verifications.count(),
        'approved_count': VerificationDocument.objects.filter(status='verified').count(),
        'rejected_count': VerificationDocument.objects.filter(status='rejected').count(),
    }
    
    return render(request, 'admin/manage_verifications.html', context)


@login_required
def approve_verification(request, doc_id):
    """Approve a verification document"""
    if not is_admin(request.user):
        return redirect('home')
    
    from accounts.models import VerificationDocument
    
    doc = get_object_or_404(VerificationDocument, id=doc_id)
    doc.status = 'verified'
    doc.verified_by = request.user
    doc.verified_at = timezone.now()
    doc.save()
    
    # Update farmer status
    farmer = doc.farmer
    farmer.farmer_verification_status = 'verified'
    farmer.kyc_verified_date = timezone.now()
    farmer.save()
    
    AdminActionLog.objects.create(
        admin=request.user,
        action_type='verification_approved',
        target_user=farmer,
        description=f"Verification approved for {farmer.username}"
    )
    
    return redirect('admin:manage_verifications')


@login_required
def activity_logs(request):
    """View admin activity logs"""
    if not is_admin(request.user):
        return redirect('home')
    
    logs = AdminActionLog.objects.select_related('admin', 'target_user').order_by('-timestamp')
    
    # Filtering
    action_type = request.GET.get('action_type')
    if action_type:
        logs = logs.filter(action_type=action_type)
    
    context = {
        'logs': logs[:500],  # Last 500 actions
        'action_filter': action_type,
    }
    
    return render(request, 'admin/activity_logs.html', context)


@login_required
def platform_analytics(request):
    """View platform-wide analytics"""
    if not is_admin(request.user):
        return redirect('home')
    
    # Get latest stats
    latest_stats = PlatformStats.objects.latest('date') if PlatformStats.objects.exists() else None
    
    # User trends (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    user_growth = User.objects.filter(date_joined__gte=thirty_days_ago).count()
    
    # Top products
    top_products = (
        Crop.objects
        .annotate(request_count=Count('purchase_requests'))
        .order_by('-request_count')[:10]
    )
    
    # Top-rated farmers
    top_farmers = (
        CustomUser.objects
        .filter(role='farmer', farmer_profile__isnull=False)
        .annotate(avg_rating=Avg('reviews_received__rating'))
        .order_by('-farmer_profile__rating_score')[:10]
    )
    
    # Risk and AI predictions
    ai_predictions = FarmerProfile.objects.select_related('user').filter(user__role='farmer').order_by('-trust_score')[:10]
    high_risk_farmers = FarmerProfile.objects.select_related('user').filter(user__role='farmer', risk_level='risky')[:10]

    context = {
        'latest_stats': latest_stats,
        'user_growth': user_growth,
        'top_products': top_products,
        'top_farmers': top_farmers,
        'ai_predictions': ai_predictions,
        'high_risk_farmers': high_risk_farmers,
    }

    return render(request, 'admin/platform_analytics.html', context)


@login_required
def ai_monitoring(request):
    """AI-powered monitoring dashboard for farmers"""
    if not is_admin(request.user):
        return redirect('home')
    
    from accounts.models import FarmerProfile
    from accounts.ml_utils import update_farmer_risk_scores
    from django.contrib import messages
    
    # Get current AI predictions
    farmers_with_ml = FarmerProfile.objects.select_related('user').filter(
        user__role='farmer'
    ).order_by('-trust_score')
    
    # Run ML update if requested
    if request.method == 'POST' and 'update_scores' in request.POST:
        try:
            results = update_farmer_risk_scores()
            messages.success(request, f'Updated ML scores for {len(results)} farmers.')
            return redirect('admin_panel:ai_monitoring')
        except Exception as e:
            messages.error(request, f'Error updating ML scores: {e}')
    
    context = {
        'trusted_farmers': farmers_with_ml.filter(risk_level='trusted'),
        'risky_farmers': farmers_with_ml.filter(risk_level='risky'),
        'moderate_farmers': farmers_with_ml.filter(risk_level='moderate'),
        'flagged_accounts': CustomUser.objects.filter(is_reported=True, role='farmer'),
        'inactive_accounts': CustomUser.objects.filter(
            role='farmer', 
            last_activity__lt=timezone.now() - timedelta(days=90)
        ),
        'auto_flagged_today': AdminActionLog.objects.filter(
            action_type='auto_flag',
            timestamp__date=timezone.now().date()
        ).count(),
        'auto_removed_today': AdminActionLog.objects.filter(
            action_type='auto_deactivate',
            timestamp__date=timezone.now().date()
        ).count(),
        'now': timezone.now(),
    }
    
    return render(request, 'admin/ai_monitoring.html', context)
