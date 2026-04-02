from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

User = get_user_model()

class CropCategory(models.Model):
    """Crop categories for organized browsing"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.ImageField(upload_to='category_icons/', blank=True, null=True)
    
    class Meta:
        verbose_name_plural = "Crop Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Crop(models.Model):
    CROP_TYPES = (
        ('legumes', 'Legumes'),
        ('cereals', 'Cereals'),
        ('vegetables', 'Vegetables'),
        ('fruits', 'Fruits'),
        ('other', 'Other'),
    )

    name = models.CharField(max_length=100)
    category = models.ForeignKey(CropCategory, on_delete=models.SET_NULL, null=True, blank=True)
    type = models.CharField(max_length=20, choices=CROP_TYPES, db_index=True)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_available = models.PositiveIntegerField()
    unit = models.CharField(max_length=20, default='kg')  # kg, bag, ton etc.
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='crops/', blank=True, null=True)
    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='crops', limit_choices_to={'role': 'farmer'})
    
    # Quality & details
    quality_grade = models.CharField(
        max_length=20,
        choices=(('premium', 'Premium'), ('standard', 'Standard'), ('regular', 'Regular')),
        default='standard'
    )
    origin = models.CharField(max_length=200, blank=True)
    harvest_date = models.DateField(null=True, blank=True)
    
    # Search & filtering
    is_organic = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['type', 'is_active']),
            models.Index(fields=['farmer_id', 'is_active']),
        ]

    def __str__(self):
        return f"{self.name} - {self.quantity_available} {self.unit} @ Ksh {self.price_per_unit}/{self.unit}"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('crop_detail', args=[str(self.id)])
    
    def get_average_rating(self):
        """Get average rating from related reviews"""
        reviews = self.reviews.filter(is_approved=True)
        if not reviews.exists():
            return 0
        return sum(r.rating for r in reviews) / reviews.count()
    
    def get_review_count(self):
        return self.reviews.filter(is_approved=True).count()


class Review(models.Model):
    """Farmer reviews from verified buyers"""
    RATING_CHOICES = (
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    )
    
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='reviews')
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_given')
    farmer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_received', limit_choices_to={'role': 'farmer'})
    
    rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    title = models.CharField(max_length=200)
    comment = models.TextField()
    
    # Verification
    purchase_request = models.ForeignKey('PurchaseRequest', on_delete=models.SET_NULL, null=True, blank=True)
    verified_purchase = models.BooleanField(default=False)
    
    # Moderation
    is_approved = models.BooleanField(default=True)
    is_flagged = models.BooleanField(default=False)
    flag_reason = models.CharField(max_length=200, blank=True)
    
    # Anti-spam
    helpful_count = models.PositiveIntegerField(default=0)
    unhelpful_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('buyer', 'farmer', 'crop')  # One review per buyer per farmer per crop
        indexes = [
            models.Index(fields=['farmer_id', 'is_approved']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.buyer.username} rated {self.farmer.username}: {self.rating}/5"


class PurchaseRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchase_requests', limit_choices_to={'role': 'buyer'})
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='purchase_requests')
    quantity_requested = models.PositiveIntegerField()
    message = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Transaction details
    agreed_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    delivery_status = models.CharField(
        max_length=20,
        choices=(('pending', 'Pending'), ('shipped', 'Shipped'), ('delivered', 'Delivered')),
        default='pending'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'buyer_id']),
        ]

    def __str__(self):
        return f"{self.buyer} requests {self.quantity_requested} {self.crop.unit} of {self.crop.name}"

    def get_total_price(self):
        price = self.agreed_price or self.crop.price_per_unit
        return self.quantity_requested * price


class SavedListing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_listings', limit_choices_to={'role': 'buyer'})
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'crop')
        ordering = ['-saved_at']
