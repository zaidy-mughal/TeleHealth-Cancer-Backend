from django.urls import path
from .views import (
    AuditLogListView,
    AuditLogDetailView,
    # audit_dashboard_view,
    # audit_statistics_view,
    # export_audit_logs_view,
)

app_name = "audits"

urlpatterns = [
    path("audit-logs/", AuditLogListView.as_view(), name="audit-log-list"),
    path(
        "audit-logs/<uuid:pk>/", AuditLogDetailView.as_view(), name="audit-log-detail"
    ),
    # path("dashboard/", audit_dashboard_view, name="audit-dashboard"),
    # path("statistics/", audit_statistics_view, name="audit-statistics"),
    # path("export/", export_audit_logs_view, name="audit-export"),
]
