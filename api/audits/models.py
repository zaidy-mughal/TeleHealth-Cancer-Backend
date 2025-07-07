import uuid
from django.db import models
from django.conf import settings

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django.utils import timezone
from api.base_models import BaseModel
from .choices import ActionTypes, StatusChoices, UserTypes


class AuditLog(BaseModel):
    """
    Audit Model to store audit logs.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="audit_logs"
    )
    user_type = models.IntegerField(choices=UserTypes.choices, default=UserTypes.ADMIN)
    full_name = models.CharField(max_length=255, null=True, blank=True)

    action = models.IntegerField(
        choices=ActionTypes.choices, default=ActionTypes.CREATE
    )
    status = models.IntegerField(
        choices=StatusChoices.choices, default=StatusChoices.SUCCESS
    )
    action_type = models.CharField(
        max_length=10, choices=ActionTypes.choices, verbose_name="Action"
    )

    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True
    )
    object_id = models.CharField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")

    resource_type = models.CharField(max_length=100)
    resource_accessed = models.CharField(max_length=255)
    resource_id = models.CharField(null=True, blank=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    session_id = models.CharField(max_length=255, null=True, blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)
    page_entry_time = models.DateTimeField(null=True, blank=True)
    page_exit_time = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.DurationField(null=True, blank=True)

    description = models.TextField(null=True, blank=True)
    changes = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "audit_logs"
        ordering = ["-timestamp"]
        indexes = [
            models.Index(fields=["user", "timestamp"]),
            models.Index(fields=["action_type", "timestamp"]),
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["resource_type", "timestamp"]),
            models.Index(fields=["ip_address", "timestamp"]),
        ]

    def __str__(self):
        return f"{self.user.username} - {dict(ActionTypes.choices)[self.action]} - {self.timestamp}"

    # def save(self, *args, **kwargs):
    #     # Allow creation of new instances
    #     if self.pk is not None:  # Check if the instance already exists
    #         raise ValueError("Audit logs are immutable and cannot be updated.")
    #     if not self.user and 'user' in kwargs:
    #         self.user = kwargs['user']
    #     if self.user and not hasattr(self, 'user_type_set'):
    #         self.user_type = UserTypes.get_user_type(self.user)
    #     super().save(*args, **kwargs)  # Call the parent save method

    # TODO for now cannot deleted but need to implement a archive way
    def delete(self, *args, **kwargs):
        raise ValueError("Audit logs are immutable and cannot be deleted.")


# TODO need to modify it more to decrease audit
class AuditLogAccess(models.Model):
    """
    Separate model to track page access patterns and time spent
    This helps avoid creating too many audit logs for simple page views
    """

    audit_log = models.ForeignKey(
        AuditLog, on_delete=models.CASCADE, related_name="access_logs"
    )
    access_time = models.DateTimeField(default=timezone.now)
    exit_time = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    page_url = models.URLField(max_length=500)

    class Meta:
        db_table = "audit_log_access"
        ordering = ["-access_time"]


class AuditLogSummary(models.Model):
    """Aggregated view for dashboard."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    user_type = models.IntegerField(choices=UserTypes.choices)
    resource_type = models.CharField(max_length=100)
    date = models.DateField()

    # Aggregated counts
    total_actions = models.PositiveIntegerField(default=0)
    create_count = models.PositiveIntegerField(default=0)
    read_count = models.PositiveIntegerField(default=0)
    update_count = models.PositiveIntegerField(default=0)
    delete_count = models.PositiveIntegerField(default=0)

    # Time tracking
    total_time_spent = models.PositiveIntegerField(default=0)  #  seconds
    first_access = models.DateTimeField()
    last_access = models.DateTimeField()

    access_times = models.JSONField(default=list)  # ["10:01", "10:05", "17:10"]

    class Meta:
        db_table = "audit_log_summary"
        unique_together = ["user", "resource_type", "date"]
        indexes = [
            models.Index(fields=["date", "user_type"]),
            models.Index(fields=["user", "date"]),
        ]


class AuditLogConfiguration(models.Model):
    """
    Configuration for audit logging rules
    """

    resource_type = models.CharField(max_length=100, unique=True)
    log_reads = models.BooleanField(default=True)
    log_creates = models.BooleanField(default=True)
    log_updates = models.BooleanField(default=True)
    log_deletes = models.BooleanField(default=True)

    deduplicate_reads_within_minutes = models.PositiveIntegerField(default=5)
    track_page_time = models.BooleanField(default=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "audit_log_configuration"

    def __str__(self):
        return f"Config for {self.resource_type}"
