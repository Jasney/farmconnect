from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('farmer', 'Farmer'),
        ('buyer', 'Buyer'),
        ('admin', 'Admin'),
    )
    
    ACCOUNT_STATUS_CHOICES = (
        ('active', 'Active'),
        ('flagged', 'Flagged'),
        ('suspended', 'Suspended'),
        ('blocked', 'Blocked'),
    )
    
    role = models.CharField(_('role'), max_length=10, choices=ROLE_CHOICES, default='buyer')
    phone = models.CharField(max_length=15, blank=True)
    location = models.CharField(max_length=200, blank=True)
    bio = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_verified = models.BooleanField(default=False, help_text="User has verified their email")
    
    # Farmer-specific fields
    national_id = models.CharField(max_length=20, blank=True, help_text="National ID number for verification")
    farmer_verification_status = models.CharField(
        max_length=20,
        choices=(
            ('pending', 'Pending Verification'),
            ('under_review', 'Under Review'),
            ('verified', 'Verified'),
            ('rejected', 'Rejected'),
        ),
        default='pending',
        null=True,
        blank=True
    )
    account_status = models.CharField(
        max_length=20,
        choices=ACCOUNT_STATUS_CHOICES,
        default='active'
    )
    kyc_document = models.FileField(upload_to='kyc_documents/', null=True, blank=True)
    kyc_verified_date = models.DateTimeField(null=True, blank=True)
    is_phone_verified = models.BooleanField(default=False)
    is_email_verified = models.BooleanField(default=False)
    
    # Activity tracking
    last_activity = models.DateTimeField(default=timezone.now)
    total_sales = models.PositiveIntegerField(default=0)  # For farmers
    total_purchases = models.PositiveIntegerField(default=0)  # For buyers
    
    # Security flags
    is_reported = models.BooleanField(default=False)
    report_count = models.PositiveIntegerField(default=0)
    suspension_reason = models.TextField(blank=True)
    suspension_until = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['role', 'account_status']),
            models.Index(fields=['last_activity']),
        ]

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_inactive(self, days=30):
        """Check if farmer/user has been inactive for specified days"""
        threshold = timezone.now() - timedelta(days=days)
        return self.last_activity < threshold
    
    def is_suspended(self):
        """Check if user is currently suspended"""
        if self.account_status == 'suspended' and self.suspension_until:
            return self.suspension_until > timezone.now()
        return self.account_status == 'suspended'
    
    def get_rating(self):
        """Get average rating from FarmerRating"""
        if self.role != 'farmer':
            return None
        try:
            return self.farmer_profile.rating_score
        except:
            return 0


class FarmerProfile(models.Model):
    """Extended profile for farmers"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='farmer_profile')
    farm_name = models.CharField(max_length=200, blank=True)
    farm_size_acres = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    years_in_business = models.PositiveIntegerField(default=0)
    
    # Ratings aggregated
    total_reviews = models.PositiveIntegerField(default=0)
    rating_score = models.DecimalField(max_digits=3, decimal_places=2, default=0)  # 0-5
    trust_score = models.DecimalField(max_digits=3, decimal_places=2, default=0)  # Calculated metric
    risk_level = models.CharField(
        max_length=20,
        choices=(
            ('trusted', 'Trusted'),
            ('risky', 'Risky'),
            ('moderate', 'Moderate'),
        ),
        default='moderate'
    )
    ml_model_updated_at = models.DateTimeField(null=True, blank=True)
    
    # Media
    farm_image = models.ImageField(upload_to='farms/', blank=True, null=True)
    
    # Stats
    total_products_sold = models.PositiveIntegerField(default=0)
    successful_transactions = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Farm Profile"


class VerificationDocument(models.Model):
    """Documents submitted for farmer KYC verification"""
    DOCUMENT_TYPES = (
        ('national_id', 'National ID'),
        ('passport', 'Passport'),
        ('tax_id', 'Tax ID'),
        ('business_permit', 'Business Permit'),
        ('land_certificate', 'Land Certificate'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    )
    
    farmer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='verification_documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    document_file = models.FileField(upload_to='verification_documents/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True)
    verified_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_documents'
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.farmer.username} - {self.get_document_type_display()}"


class FarmerReview(models.Model):
    """Reviews for farmers from buyers after successful transactions"""
    RATING_CHOICES = (
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    )
    
    farmer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='farmer_reviews', limit_choices_to={'role': 'farmer'})
    buyer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='buyer_reviews', limit_choices_to={'role': 'buyer'})
    transaction = models.ForeignKey('crops.PurchaseRequest', on_delete=models.CASCADE, related_name='reviews')
    
    rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    title = models.CharField(max_length=200)
    comment = models.TextField()
    
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('buyer', 'farmer', 'transaction')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.buyer.username} reviewed {self.farmer.username}: {self.rating} stars"





