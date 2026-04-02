from django.db import models
from django.utils import timezone

class MarketPrice(models.Model):
    crop_name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20, default='kg')
    updated_at = models.DateTimeField(default=timezone.now)
    location = models.CharField(max_length=100, blank=True, db_index=True)

    class Meta:
        ordering = ['-updated_at']
        unique_together = ('crop_name', 'location')

    def __str__(self):
        return f"{self.crop_name}: Ksh {self.price}/{self.unit}"

