from django.contrib import admin
from api.audits.models import AuditLog, AuditLogSummary


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "action", "resource_type", "timestamp"]
    list_filter = ["action", "resource_type"]

    search_fields = ("user__email", "action", "resource_type")
    ordering = ("-timestamp",)
    readonly_fields = ("id",)


@admin.register(AuditLogSummary)
class AuditLogSummaryAdmin(admin.ModelAdmin):
    list_display = ["user", "resource_type", "date", "total_actions"]
    list_filter = ["user", "resource_type", "date"]

    search_fields = ("user__email", "resource_type")
    ordering = ("-date",)
