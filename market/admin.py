from django.contrib import admin
from .models import MarketPrice

@admin.register(MarketPrice)
class MarketPriceAdmin(admin.ModelAdmin):
    list_display = ['crop_name', 'price', 'unit', 'location', 'updated_at']
    list_filter = ['location']
    search_fields = ['crop_name', 'location']
