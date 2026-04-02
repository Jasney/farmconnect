from django.contrib import admin
from .models import (
    UserReport, AdminActionLog, FarmerActivityMetric,
    InactiveAccountFlag, SystemAuditLog, PlatformStats
)

@admin.register(UserReport)
class UserReportAdmin(admin.ModelAdmin):
    list_display = ('reported_user', 'report_type', 'severity', 'status', 'created_at')
    list_filter = ('status', 'severity', 'report_type', 'created_at')
    search_fields = ('reported_user__username', 'title', 'description')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(AdminActionLog)
class AdminActionLogAdmin(admin.ModelAdmin):
    list_display = ('admin', 'action_type', 'target_user', 'timestamp')
    list_filter = ('action_type', 'timestamp')
    search_fields = ('admin__username', 'target_user__username')
    readonly_fields = ('timestamp', 'admin')

@admin.register(FarmerActivityMetric)
class FarmerActivityMetricAdmin(admin.ModelAdmin):
    list_display = ('farmer', 'date', 'products_listed', 'purchase_requests_received')
    list_filter = ('date',)
    search_fields = ('farmer__username',)

@admin.register(InactiveAccountFlag)
class InactiveAccountFlagAdmin(admin.ModelAdmin):
    list_display = ('farmer', 'status', 'flagged_at', 'days_inactive')
    list_filter = ('status', 'flagged_at')
    search_fields = ('farmer__username',)

@admin.register(SystemAuditLog)
class SystemAuditLogAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'user', 'timestamp')
    list_filter = ('event_type', 'timestamp')
    search_fields = ('user__username', 'description')
    readonly_fields = ('timestamp',)

@admin.register(PlatformStats)
class PlatformStatsAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_users', 'total_products', 'completed_purchases')
    list_filter = ('date',)
    readonly_fields = ('date',)
