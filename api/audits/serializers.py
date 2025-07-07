from rest_framework import serializers
from api.audits.models import (
    AuditLog,
    AuditLogAccess,
    AuditLogSummary,
    AuditLogConfiguration,
)

from django.utils import timezone
from datetime import timedelta
from collections import defaultdict


class AuditLogListSerializer(serializers.ModelSerializer):
    """
    Dashboard list view
    """

    user_name = serializers.CharField(source="full_name", read_only=True)
    date = serializers.DateTimeField(
        source="timestamp", format="%b %d, %Y, %I:%M %p", read_only=True
    )
    action_type_display = serializers.CharField(
        source="get_action_type_display", read_only=True
    )
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    user_type_display = serializers.CharField(
        source="get_user_type_display", read_only=True
    )

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "date",
            "action",
            "resource_type",
            "user_type_display",
            "user_name",
            "action_type_display",
            "status_display",
        ]


class AuditLogDetailSerializer(serializers.ModelSerializer):

    user_info = serializers.SerializerMethodField()
    action_details = serializers.SerializerMethodField()
    resource_information = serializers.SerializerMethodField()
    additional_information = serializers.SerializerMethodField()
    access_logs = serializers.SerializerMethodField()

    class Meta:
        model = AuditLog
        fields = [
            "id",
            "user_info",
            "action_details",
            "resource_information",
            "additional_information",
            "access_logs",
        ]

    def get_user_info(self, obj):
        return {
            "user": obj.full_name,
            "user_type": obj.get_user_type_display(),
            "ip_address": obj.ip_address,
            "user_agent": obj.user_agent,
            "session_id": obj.session_id,
        }

    def get_action_details(self, obj):
        return {
            "action": obj.action,
            "action_type": obj.get_action_type_display(),
            "date_time": obj.timestamp.strftime("%b %d, %Y, %I:%M:%S %p"),
            "status": obj.get_status_display(),
        }

    def get_resource_information(self, obj):
        return {
            "resource_type": obj.resource_type,
            "resource_accessed": obj.resource_accessed,
            "resource_id": obj.resource_id,
        }

    def get_additional_information(self, obj):
        additional_info = {
            "description": obj.description,
        }

        if obj.changes:
            additional_info["changes"] = obj.changes

        if obj.duration_seconds:
            additional_info["time_spent"] = self._format_duration(obj.duration_seconds)

        return additional_info

    def get_access_logs(self, obj):
        access_logs = obj.access_logs.all()
        return [
            {
                "access_time": access.access_time.strftime("%b %d, %Y, %I:%M:%S %p"),
                "duration": (
                    self._format_duration(access.duration_seconds)
                    if access.duration_seconds
                    else None
                ),
                "page_url": access.page_url,
            }
            for access in access_logs
        ]

    def _format_duration(self, seconds):

        if not seconds:
            return None
        total_seconds = (
            seconds.total_seconds() if hasattr(seconds, "total_seconds") else seconds
        )
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        secs = total_seconds % 60
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"


# TODO need modifications according to requirement in future
class AuditLogDashboardSerializer(serializers.Serializer):
    """
    Serializer for dashboard aggregated view
    """

    user = serializers.CharField()
    user_type = serializers.CharField()
    date = serializers.DateField()
    times = serializers.ListField(child=serializers.CharField())
    count = serializers.IntegerField()
    total_time_spent = serializers.CharField()
    resource_types = serializers.ListField(child=serializers.CharField())
    actions = serializers.SerializerMethodField()

    def get_actions(self, obj):
        """Get breakdown of actions by type"""
        return {
            "create": obj.get("create_count", 0),
            "read": obj.get("read_count", 0),
            "update": obj.get("update_count", 0),
            "delete": obj.get("delete_count", 0),
        }


# TODO Currently not using but can be needed if not implment middleware
class AuditLogCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating audit logs
    """

    user_agent = serializers.CharField(required=False)
    ip_address = serializers.IPAddressField(required=False)
    session_id = serializers.CharField(required=False)

    class Meta:
        model = AuditLog
        fields = [
            "user",
            "user_type",
            "action",
            "action_type",
            "resource_type",
            "resource_accessed",
            "resource_id",
            "description",
            "changes",
            "status",
            "ip_address",
            "user_agent",
            "session_id",
            "page_entry_time",
        ]

    def create(self, validated_data):
        request = self.context.get("request")
        if request:
            if not validated_data.get("ip_address"):
                validated_data["ip_address"] = self._get_client_ip(request)
            if not validated_data.get("user_agent"):
                validated_data["user_agent"] = request.META.get("HTTP_USER_AGENT", "")
            if not validated_data.get("session_id"):
                validated_data["session_id"] = request.session.session_key
        return super().create(validated_data)

    def _get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        return (
            x_forwarded_for.split(",")[0]
            if x_forwarded_for
            else request.META.get("REMOTE_ADDR")
        )


class AuditLogAccessSerializer(serializers.ModelSerializer):

    class Meta:
        model = AuditLogAccess
        fields = [
            "audit_log",
            "access_time",
            "exit_time",
            "duration_seconds",
            "page_url",
        ]


class AuditLogSummarySerializer(serializers.ModelSerializer):

    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    user_type_display = serializers.CharField(
        source="get_user_type_display", read_only=True
    )
    total_time_formatted = serializers.SerializerMethodField()

    class Meta:
        model = AuditLogSummary
        fields = [
            "user_name",
            "user_type_display",
            "resource_type",
            "date",
            "total_actions",
            "create_count",
            "read_count",
            "update_count",
            "delete_count",
            "total_time_formatted",
            "first_access",
            "last_access",
            "access_times",
        ]

    def get_total_time_formatted(self, obj):
        """Format total time spent"""
        seconds = obj.total_time_spent
        if not seconds:
            return "0s"
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        if hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"


class AuditLogConfigurationSerializer(serializers.ModelSerializer):

    class Meta:
        model = AuditLogConfiguration
        fields = "__all__"


# TODO future modification
class AuditLogStatsSerializer(serializers.Serializer):

    total_logs = serializers.IntegerField()
    logs_today = serializers.IntegerField()
    logs_this_week = serializers.IntegerField()
    logs_this_month = serializers.IntegerField()
    top_users = serializers.ListField(child=serializers.DictField())
    action_breakdown = serializers.DictField()
    recent_activities = serializers.ListField(child=serializers.DictField())
    failed_actions = serializers.IntegerField()
    avg_session_duration = serializers.CharField()


# Utility functions
def get_dashboard_data(start_date=None, end_date=None, user_type=None):

    if not start_date:
        start_date = timezone.now().date() - timedelta(days=30)
    if not end_date:
        end_date = timezone.now().date()

    queryset = AuditLog.objects.filter(timestamp__date__range=[start_date, end_date])
    if user_type:
        queryset = queryset.filter(user_type=user_type)

    dashboard_data = []
    user_date_groups = defaultdict(lambda: defaultdict(list))

    for log in queryset.select_related("user"):
        key = (
            log.user.get_full_name() or log.user.username,
            log.user_type,
            log.timestamp.date(),
        )
        user_date_groups[key[:2]][key[2]].append(log)

    for (user_name, user_type), date_logs in user_date_groups.items():
        for date, logs in date_logs.items():
            times = [log.timestamp.strftime("%H:%M") for log in logs]
            total_duration = sum(
                log.duration_seconds.total_seconds() if log.duration_seconds else 0
                for log in logs
            )
            resource_types = list(set(log.resource_type for log in logs))
            action_counts = {
                "create_count": len([l for l in logs if l.action_type == "CREATE"]),
                "read_count": len([l for l in logs if l.action_type == "READ"]),
                "update_count": len([l for l in logs if l.action_type == "UPDATE"]),
                "delete_count": len([l for l in logs if l.action_type == "DELETE"]),
            }
            dashboard_data.append(
                {
                    "user": user_name,
                    "user_type": user_type,
                    "date": date,
                    "times": times,
                    "count": len(logs),
                    "total_time_spent": _format_duration(total_duration),
                    "resource_types": resource_types,
                    **action_counts,
                }
            )

    return dashboard_data


def _format_duration(seconds):

    if not seconds:
        return "0s"
    hours = int(seconds) // 3600
    minutes = (int(seconds) % 3600) // 60
    secs = int(seconds) % 60
    if hours > 0:
        return f"{hours}h {minutes}m"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = "__all__"
