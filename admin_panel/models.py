from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class UserReport(models.Model):
    """Reports of suspicious or problematic user activity"""
    REPORT_TYPES = (
        ('fraud', 'Fraudulent Activity'),
        ('inappropriate_content', 'Inappropriate Content'),
        ('harassment', 'Harassment/Abuse'),
        ('failed_transaction', 'Failed Transaction'),
        ('non_delivery', 'Non-Delivery'),
        ('quality_issue', 'Quality Issue'),
        ('other', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('investigating', 'Investigating'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    )
    
    reported_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_against')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_submitted')
    report_type = models.CharField(max_length=30, choices=REPORT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    evidence_attachment = models.FileField(upload_to='report_evidence/', blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    severity = models.CharField(
        max_length=10,
        choices=(('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')),
        default='medium'
    )
    
    admin_notes = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reports_reviewed')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['reported_user_id', 'status']),
            models.Index(fields=['severity', 'status']),
        ]

    def __str__(self):
        return f"Report: {self.reported_user.username} - {self.get_report_type_display()}"


class AdminActionLog(models.Model):
    """Audit log of all admin actions taken on the system"""
    ACTION_TYPES = (
        ('user_flagged', 'User Flagged'),
        ('user_suspended', 'User Suspended'),
        ('user_blocked', 'User Blocked'),
        ('user_unsuspended', 'User Unsuspended'),
        ('user_deleted', 'User Deleted'),
        ('verification_approved', 'Verification Approved'),
        ('verification_rejected', 'Verification Rejected'),
        ('review_removed', 'Review Removed'),
        ('message_deleted', 'Message Deleted'),
        ('conversation_blocked', 'Conversation Blocked'),
        ('farmer_removed', 'Farmer Removed'),
        ('admin_added', 'Admin Added'),
        ('settings_changed', 'Settings Changed'),
        ('report_resolved', 'Report Resolved'),
        ('appeal_submitted', 'Appeal Submitted'),
        ('appeal_resolved', 'Appeal Resolved'),
        ('other', 'Other'),
    )
    
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='admin_actions')
    action_type = models.CharField(max_length=30, choices=ACTION_TYPES)
    target_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='admin_actions_against')
    
    description = models.TextField()
    reason = models.TextField(blank=True)
    
    # Related objects
    related_report = models.ForeignKey(UserReport, on_delete=models.SET_NULL, null=True, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['admin_id', 'timestamp']),
            models.Index(fields=['action_type', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.admin.username if self.admin else 'System'}: {self.get_action_type_display()}"


class AccountAppeal(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appeals')
    issue_summary = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='appeals_reviewed')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Appeal #{self.id} - {self.farmer.username} ({self.get_status_display()})"


class FarmerActivityMetric(models.Model):
    """Daily/weekly metrics for farmer activity for analytics"""
    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activity_metrics')
    date = models.DateField(db_index=True)
    
    # Activity
    products_listed = models.PositiveIntegerField(default=0)
    purchase_requests_received = models.PositiveIntegerField(default=0)
    purchase_requests_accepted = models.PositiveIntegerField(default=0)
    messages_sent = models.PositiveIntegerField(default=0)
    messages_received = models.PositiveIntegerField(default=0)
    
    # Engagement
    profile_views = models.PositiveIntegerField(default=0)
    product_views = models.PositiveIntegerField(default=0)
    
    # Rating
    reviews_received = models.PositiveIntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    
    # Flags
    reports_filed = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        unique_together = ('farmer', 'date')
        indexes = [
            models.Index(fields=['farmer_id', 'date']),
        ]

    def __str__(self):
        return f"Metrics for {self.farmer.username} on {self.date}"


class InactiveAccountFlag(models.Model):
    """Track and flag inactive farmer accounts"""
    farmer = models.OneToOneField(User, on_delete=models.CASCADE, related_name='inactive_flag')
    flagged_at = models.DateTimeField(auto_now_add=True)
    days_inactive = models.PositiveIntegerField(default=30)
    last_checked = models.DateTimeField(auto_now=True)
    
    # Action tracking
    warning_sent = models.BooleanField(default=False)
    warning_sent_at = models.DateTimeField(null=True, blank=True)
    removal_scheduled = models.BooleanField(default=False)
    removal_date = models.DateTimeField(null=True, blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=(
            ('flagged', 'Flagged'),
            ('warning_sent', 'Warning Sent'),
            ('reactivated', 'Reactivated'),
            ('removed', 'Removed'),
        ),
        default='flagged'
    )

    class Meta:
        verbose_name = "Inactive Account Flag"

    def __str__(self):
        return f"Inactive flag for {self.farmer.username}"


class SystemAuditLog(models.Model):
    """General system audit log for all significant events"""
    EVENT_TYPES = (
        ('account_created', 'Account Created'),
        ('account_deleted', 'Account Deleted'),
        ('login', 'Login'),
        ('password_changed', 'Password Changed'),
        ('verification_submitted', 'Verification Submitted'),
        ('review_posted', 'Review Posted'),
        ('message_sent', 'Message Sent'),
        ('purchase_completed', 'Purchase Completed'),
        ('account_flagged', 'Account Flagged'),
        ('system_alert', 'System Alert'),
    )
    
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['event_type', 'timestamp']),
            models.Index(fields=['user_id', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.get_event_type_display()} - {self.user if self.user else 'System'}"


class PlatformStats(models.Model):
    """Overall platform statistics for dashboard"""
    date = models.DateField(auto_now_add=True, unique=True)
    
    # Users
    total_users = models.PositiveIntegerField(default=0)
    total_farmers = models.PositiveIntegerField(default=0)
    total_buyers = models.PositiveIntegerField(default=0)
    new_users_today = models.PositiveIntegerField(default=0)
    
    # Products
    total_products = models.PositiveIntegerField(default=0)
    new_products_today = models.PositiveIntegerField(default=0)
    
    # Transactions
    total_purchases = models.PositiveIntegerField(default=0)
    completed_purchases = models.PositiveIntegerField(default=0)
    purchase_value_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Engagement
    messages_sent = models.PositiveIntegerField(default=0)
    reviews_posted = models.PositiveIntegerField(default=0)
    reports_filed = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Platform Stats for {self.date}"
