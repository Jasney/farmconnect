from django.contrib import admin
from .models import Crop, SavedListing, PurchaseRequest

@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    list_display = ['name', 'type', 'price_per_unit', 'quantity_available', 'farmer', 'is_active']
    list_filter = ['type', 'is_active']
    search_fields = ['name', 'description', 'farmer__username']


@admin.register(SavedListing)
class SavedListingAdmin(admin.ModelAdmin):
    list_display = ['user', 'crop', 'saved_at']


@admin.register(PurchaseRequest)
class PurchaseRequestAdmin(admin.ModelAdmin):
    list_display = ['buyer', 'crop', 'quantity_requested', 'status', 'created_at']
    list_filter = ['status', 'crop__farmer']
    search_fields = ['buyer__username', 'crop__name']
