import logging

from django.core.exceptions import ValidationError
from .models import AuditLog
from .choices import ActionTypes

logger = logging.getLogger(__name__)

AUDIT_PATHS = [
    "/api/appointments/",
    "/api/appointments/create/",
    "/api/patients/",
    "/api/doctors/",
    "/api/payments/stripe/refund/",
]

SKIP_PATHS = [
    "/api/auth/refresh/",
    "/api/auth/token/",
    "/api/health/",
    "/api/audit-logs/",
    "/api/webhooks/payment-intent/",
    "/api/webhooks/",
]


def validate_audit_request(request):

    path = request.path
    logger.info(f"Validating audit request for path: {path}")
    if any(path.startswith(skip_path) for skip_path in SKIP_PATHS):
        return False
    if any(path.startswith(audit_path) for audit_path in AUDIT_PATHS):
        return True
    return False


def validate_action_type(method):

    action_type_map = {
        "GET": ActionTypes.READ,
        "POST": ActionTypes.CREATE,
        "PUT": ActionTypes.UPDATE,
        "PATCH": ActionTypes.UPDATE,
        "DELETE": ActionTypes.DELETE,
    }
    action_type = action_type_map.get(method)
    if action_type is None:
        raise ValidationError(f"Unsupported HTTP method: {method}")
    return action_type


def validate_resource_info(path, request):
    """Resource mappings details"""

    resource_mappings = {
        "/api/patients/": {
            "resource_type": "Patient Records",
            "resource_accessed": "Patient Management System",
            "action_templates": {
                "GET": "Accessed patient record",
                "POST": "Created patient record",
                "PUT": "Updated patient information",
                "PATCH": "Modified patient information",
                "DELETE": "Deleted patient record",
            },
        },
        "/api/appointments/": {
            "resource_type": "Appointment System",
            "resource_accessed": "Appointment Management System",
            "action_templates": {
                "GET": "Accessed appointment",
                "POST": "Created appointment",
                "PUT": "Updated appointment",
                "PATCH": "Rescheduled appointment",
                "DELETE": "Deleted appointment",
            },
        },
        "/api/doctors/": {
            "resource_type": "Doctor Records",
            "resource_accessed": "Doctor Management System",
            "action_templates": {
                "GET": "Accessed doctor information",
                "POST": "Created doctor profile",
                "PUT": "Updated doctor information",
                "PATCH": "Modified doctor information",
                "DELETE": "Deleted doctor profile",
            },
        },
        "/api/auth/": {
            "resource_type": "Authentication System",
            "resource_accessed": "Authentication System",
            "action_templates": {
                "POST": "User logged in" if "login" in path else "User action",
                "DELETE": "User logged out",
            },
        },
        "/api/users/": {
            "resource_type": "User Management",
            "resource_accessed": "User Management System",
            "action_templates": {
                "GET": "Accessed user information",
                "POST": "Created user",
                "PUT": "Updated user information",
                "PATCH": "Modified user information",
                "DELETE": "Deleted user",
            },
        },
    }
    for pattern, info in resource_mappings.items():
        if path.startswith(pattern):
            action_template = info["action_templates"].get(
                request.method, "Unknown action"
            )
            resource_id = path.split("/")[-1] if path.count("/") > 3 else None
            return {
                "action": action_template,
                "resource_type": info["resource_type"],
                "resource_accessed": info["resource_accessed"],
                "resource_id": resource_id,
            }
    return None


def validate_duration(start_time):

    from time import time

    end_time = time()
    return int((end_time - start_time) * 1000)
