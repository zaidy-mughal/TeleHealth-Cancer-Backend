import time
import json
import logging
from uuid import UUID

from .choices import StatusChoices

from django.utils import timezone
from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.models import ContentType

from .models import AuditLog, AuditLogConfiguration
from .validators import (
    validate_audit_request,
    validate_action_type,
    validate_duration,
    validate_resource_info,
)

logger = logging.getLogger(__name__)


class AuditLogMiddleware:
    """Using Middleware for audit logs"""

    def __init__(self, get_response):
        logger.info("Initializing AuditLogMiddleware")
        self.get_response = get_response
        self.config_cache = {}
        self._load_configurations()

    def _load_configurations(self):
        """Load audit configurations in cache to save db hits"""
        try:
            configs = AuditLogConfiguration.objects.filter(is_active=True)
            for config in configs:
                self.config_cache[config.resource_type] = config
        except Exception as e:
            logger.warning(f"Unable to load audit configurations: {e}")

    def _get_audit_log_request_info(self, request):
        """Audit log information required from requests"""

        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        ip_address = (
            x_forwarded_for.split(",")[0].strip()
            if x_forwarded_for
            else request.META.get("REMOTE_ADDR")
        )
        user_agent = request.META.get("HTTP_USER_AGENT", "")
        session_id = (
            request.session.session_key if hasattr(request, "session") else None
        )
        return ip_address, user_agent, session_id

    # TODO (In future) need to use the users choices to more improve it
    def _get_user_type(self, user):

        user_types = {
            "admin": 1,
            "doctor": 2,
            "nurse": 3,
        }
        return user_types.get(
            user.groups.first().name.lower() if user.groups.exists() else "admin", 1
        )

    def _get_full_name(self, user):

        return (
            f"{user.first_name or ''} {user.last_name or ''}".strip() or user.username
        )

    def __call__(self, request):

        self._process_incoming_request(request)

        response = self.get_response(request)

        response = self._process_outgoing_response(request, response)

        return response

    def _process_incoming_request(self, request):
        """Handle request processing"""

        logger.info("AuditlogMiddleware: Processing request")
        request._audit_start_time = time.time()
        ip_address, user_agent, session_id = self._get_audit_log_request_info(request)
        request._audit_data = {
            "ip_address": ip_address,
            "user_agent": user_agent,
            "session_id": session_id,
            "url": request.get_full_path(),
            "method": request.method,
        }

        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                if request.content_type == "application/json":
                    request._audit_request_body = json.loads(
                        request.body.decode("utf-8")
                    )
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                logger.warning(f"Error in methods: {e}")
                request._audit_request_body = None

    def _process_outgoing_response(self, request, response):
        """Handle response processing"""

        if isinstance(request.user, AnonymousUser):
            logger.debug("Skipping audit log: Anonymous user")
            return response

        if not validate_audit_request(request):
            logger.debug(f"Skipping audit log: Path {request.path} not audited")
            return response

        try:
            duration = validate_duration(request._audit_start_time)
            action_info = self._analyze_request(request, response)

            if (
                request.method == "POST"
                and request.path == "/api/appointments/create/"
                and response.status_code == 201
            ):
                try:
                    response_data = json.loads(response.content)
                    action_info["resource_id"] = response_data.get("uuid")
                except json.JSONDecodeError:
                    logger.warning("Could not parse appointment creation response")

            if action_info and self._should_log_action(
                action_info["resource_type"], action_info["action_type"], request.user
            ):
                self._create_audit_entry(request, response, action_info, duration)

        except Exception as e:
            logger.error(f"Error creating audit log: {e}", exc_info=True)
            if not hasattr(request, "_audit_start_time"):
                request._audit_start_time = time.time()

        return response

    def _should_log_action(self, resource_type, action_type, user):
        config = self.config_cache.get(resource_type)
        return config is None or config.is_active

    def _analyze_request(self, request, response):
        """Analyze request to determine audit log details"""
        method = request.method
        logger.info(f"Request method: {method}")
        action_type = validate_action_type(method)
        resource_info = validate_resource_info(request.path, request)

        if not resource_info:
            logger.warning(f"No resource info for path: {request.path}")
            return None

        status = "SUCCESS" if 200 <= response.status_code < 300 else "FAILED"
        changes = (
            request._audit_request_body
            if hasattr(request, "_audit_request_body")
            else None
        )

        action_info = {
            "action": resource_info["action"],
            "action_type": action_type,
            "resource_type": resource_info["resource_type"],
            "resource_accessed": resource_info["resource_accessed"],
            "resource_id": resource_info.get("resource_id"),
            "status": status,
            "changes": changes,
            "description": f"{resource_info['action']} - {status}",
        }

        logger.info(f"Analyzing request: {request.path}, Action: {action_info}")
        return action_info

    def _create_audit_entry(self, request, response, action_info, duration):
        try:
            logger.info(f"Creating audit log for action: {action_info['action']}")

            appointment_uuid = None
            resource_id = action_info.get("resource_id")
            if (
                request.method in ["GET", "PUT", "DELETE"]
                and "create" not in request.path
            ):
                try:
                    potential_id = request.path.rstrip("/").split("/")[-1]
                    if potential_id.isdigit():
                        resource_id = int(potential_id)
                    else:
                        UUID(potential_id)
                        appointment_uuid = potential_id
                    logger.info(
                        f"Resource ID: {resource_id}, Appointment UUID: {appointment_uuid}"
                    )
                except ValueError:
                    logger.debug(f"No valid ID or UUID found in path: {request.path}")
                    appointment_uuid = None
                    resource_id = resource_id if resource_id else None

            try:
                content_type = ContentType.objects.get(model="appointment")
            except ContentType.DoesNotExist:
                content_type = None

            AuditLog.objects.create(
                user=request.user,
                user_type=self._get_user_type(request.user),
                full_name=self._get_full_name(request.user),
                action=action_info["action_type"],
                action_type=action_info["action_type"],
                status=(
                    StatusChoices.SUCCESS
                    if action_info["status"] == "SUCCESS"
                    else StatusChoices.FAILURE
                ),
                content_type=content_type,
                object_id=appointment_uuid,
                resource_type=action_info["resource_type"],
                resource_accessed=action_info["resource_accessed"],
                resource_id=(
                    resource_id
                    if resource_id
                    and (isinstance(resource_id, int) or resource_id.isdigit())
                    else None
                ),
                ip_address=request._audit_data["ip_address"],
                user_agent=request._audit_data["user_agent"],
                session_id=request._audit_data["session_id"],
                timestamp=timezone.now(),
                duration_seconds=timezone.timedelta(milliseconds=duration),
                page_entry_time=timezone.now(),
                page_exit_time=timezone.now(),
                description=action_info["description"],
                changes=action_info.get("changes") or {},
            )
            logger.info(f"Audit log created for path: {request.path}")
        except Exception as e:
            logger.error(f"Failed to create audit log: {e}", exc_info=True)
