import pytest
from django.test import RequestFactory
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse, resolve
from django.utils import timezone
from django.contrib.sessions.backends.db import SessionStore
from datetime import timedelta
from api.audits.models import AuditLog, StatusChoices
from api.audits.middleware import AuditLogMiddleware
from api.audits.serializers import AuditLogListSerializer, AuditLogDetailSerializer
from api.audits.validators import (
    validate_audit_request,
    validate_action_type,
    validate_resource_info,
    validate_duration,
)
import logging
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from api.audits.choices import ActionTypes, StatusChoices
from unittest.mock import patch

logger = logging.getLogger(__name__)


def test_sample():
    assert True


@pytest.fixture
def api_client(db):
    client = APIClient()
    user = get_user_model().objects.create_user(
        email="testuser@example.com",
        password="testpass",
        first_name="Test",
        last_name="User",
    )
    client.force_authenticate(user=user)
    yield client
    user.delete()


@pytest.fixture
def factory():
    return RequestFactory()


@pytest.fixture
def authenticated_request(factory, db):
    user = get_user_model().objects.create_user(
        email="testuser@example.com", password="testpass"
    )
    request = factory.get("/api/appointments/123/")
    request.user = user
    request._audit_start_time = timezone.now().timestamp()
    request.session = SessionStore()
    request.session["session_key"] = "test_session"
    request.session.save()
    yield request
    user.delete()


@pytest.mark.django_db
def test_validate_audit_request(factory):
    request = factory.get("/api/appointments/")
    assert validate_audit_request(request) is True

    request = factory.get("/api/auth/token/")
    assert validate_audit_request(request) is False

    request = factory.get("/api/other/")
    assert validate_audit_request(request) is False


@pytest.mark.django_db
def test_validate_action_type():
    assert validate_action_type("GET") == ActionTypes.READ
    assert validate_action_type("POST") == ActionTypes.CREATE
    with pytest.raises(Exception):
        validate_action_type("INVALID")


@pytest.mark.django_db
def test_validate_resource_info(factory):
    request = factory.get("/api/appointments/123/")
    result = validate_resource_info(request.path, request)
    assert result["resource_type"] == "Appointment System"
    assert result["action"] == "Accessed appointment"
    assert result["resource_id"] == "123"

    request = factory.get("/api/auth/")
    result = validate_resource_info(request.path, request)
    assert result["resource_type"] == "Authentication System"

    request = factory.get("/api/other/")
    assert validate_resource_info(request.path, request) is None


@pytest.mark.django_db
def test_validate_duration():
    start_time = timezone.now().timestamp()
    with patch("time.time", return_value=start_time + 0.015):
        duration = validate_duration(start_time)
        assert isinstance(duration, int)
        assert duration == 15


# --- Serializers Tests ---
@pytest.mark.django_db
def test_audit_log_list_serializer(db):
    AuditLog.objects.all().delete()  # Clear database
    user = get_user_model().objects.create_user(
        email="testuser@example.com", first_name="Test", last_name="User"
    )
    audit_log = AuditLog.objects.create(
        user=user,
        action=ActionTypes.CREATE,
        action_type=ActionTypes.CREATE,
        resource_type="Appointment System",
        full_name="Test User",
        status=StatusChoices.SUCCESS,
        user_type=1,
    )
    serializer = AuditLogListSerializer(audit_log)
    data = serializer.data
    assert data["user_name"] == "Test User"
    assert "date" in data
    assert data["action_type_display"] == "Create"

    audit_log.full_name = ""
    serializer = AuditLogListSerializer(audit_log)
    assert serializer.data["user_name"] == ""
    user.delete()


@pytest.mark.django_db
def test_audit_log_detail_serializer(db):
    AuditLog.objects.all().delete()
    user = get_user_model().objects.create_user(
        email="testuser@example.com", first_name="Test", last_name="User"
    )
    audit_log = AuditLog.objects.create(
        user=user,
        action=ActionTypes.CREATE,
        action_type=ActionTypes.CREATE,
        resource_type="Appointment System",
        full_name="Test User",
        status=StatusChoices.SUCCESS,
        ip_address="192.168.1.1",
        user_agent="TestAgent",
        session_id="sess_123",
        timestamp=timezone.now(),
        duration_seconds=timedelta(seconds=10),
        description="Test action",
        user_type=1,
    )
    serializer = AuditLogDetailSerializer(audit_log)
    data = serializer.data
    assert data["user_info"]["user"] == "Test User"
    assert data["action_details"]["action_type"] == "Create"
    assert data["resource_information"]["resource_type"] == "Appointment System"
    assert data["additional_information"]["time_spent"] == "10s"

    audit_log.duration_seconds = None
    serializer = AuditLogDetailSerializer(audit_log)
    assert "time_spent" not in serializer.data["additional_information"]
    user.delete()


# --- Middleware Tests ---
@pytest.mark.django_db
def test_audit_log_middleware(authenticated_request, db):
    from rest_framework.response import Response

    AuditLog.objects.all().delete()
    middleware = AuditLogMiddleware(lambda r: Response())
    middleware.process_request(authenticated_request)
    assert hasattr(authenticated_request, "_audit_data")
    assert authenticated_request._audit_data["ip_address"]
    assert authenticated_request._audit_data["session_id"]

    response = middleware.process_response(authenticated_request, Response())
    audit_log = AuditLog.objects.filter(user=authenticated_request.user).first()
    assert audit_log is not None
    assert audit_log.action == ActionTypes.READ
    assert audit_log.resource_id is None

    authenticated_request.user = AnonymousUser()
    response = middleware.process_response(authenticated_request, Response())
    assert not AuditLog.objects.filter(user=None).exists()


# --- Views Tests ---
@pytest.mark.django_db
def test_audit_log_list_view(api_client, db):
    AuditLog.objects.all().delete()
    user = get_user_model().objects.get(email="testuser@example.com")
    AuditLog.objects.create(
        user=user,
        action=ActionTypes.CREATE,
        action_type=ActionTypes.CREATE,
        resource_type="Appointment System",
        full_name="Test User",
        status=StatusChoices.SUCCESS,
        user_type=1,
    )
    AuditLog.objects.create(
        user=user,
        action=ActionTypes.READ,
        action_type=ActionTypes.READ,
        resource_type="Patient Records",
        full_name="Test User",
        status=StatusChoices.FAILURE,
        user_type=1,
    )

    url = reverse("audits:audit-log-list")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 2
    assert "total_count" in response.data

    response = api_client.get(url + "?start_date=invalid")
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data["results"]) == 2

    response = api_client.get(url + "?page_size=200")
    assert len(response.data["results"]) <= 100


@pytest.mark.django_db
def test_audit_log_detail_view(api_client, db):
    AuditLog.objects.all().delete()
    user = get_user_model().objects.get(email="testuser@example.com")
    audit_log = AuditLog.objects.create(
        user=user,
        action=ActionTypes.CREATE,
        action_type=ActionTypes.CREATE,
        resource_type="Appointment System",
        full_name="Test User",
        status=StatusChoices.SUCCESS,
        user_type=1,
    )

    url = reverse("audits:audit-log-detail", kwargs={"pk": audit_log.id})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert "user_info" in response.data
    assert AuditLog.objects.filter(action=ActionTypes.READ).count() >= 1

    invalid_url = reverse("audits:audit-log-detail", kwargs={"pk": 9999})
    response = api_client.get(invalid_url)
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_audit_dashboard_view(api_client, db):
    AuditLog.objects.all().delete()
    user = get_user_model().objects.get(email="testuser@example.com")
    AuditLog.objects.create(
        user=user,
        action=ActionTypes.CREATE,
        action_type=ActionTypes.CREATE,
        resource_type="Appointment System",
        full_name="Test User",
        status=StatusChoices.SUCCESS,
        user_type=1,
    )

    url = reverse("audits:audit-dashboard")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert "results" in response.data

    response = api_client.get(url + "?start_date=invalid&end_date=2025-07-01")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_audit_statistics_view(api_client, db):
    AuditLog.objects.all().delete()
    user = get_user_model().objects.get(email="testuser@example.com")
    AuditLog.objects.create(
        user=user,
        action=ActionTypes.CREATE,
        action_type=ActionTypes.CREATE,
        resource_type="Appointment System",
        full_name="Test User",
        status=StatusChoices.SUCCESS,
        user_type=1,
    )

    url = reverse("audits:audit-statistics")
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert "total_logs" in response.data

    response = api_client.get(url + "?days=invalid")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_export_audit_logs_view(api_client, db):
    AuditLog.objects.all().delete()
    user = get_user_model().objects.get(email="testuser@example.com")
    AuditLog.objects.create(
        user=user,
        action=ActionTypes.CREATE,
        action_type=ActionTypes.CREATE,
        resource_type="Appointment System",
        full_name="Test User",
        status=StatusChoices.SUCCESS,
        user_type=1,
    )

    url = reverse("audits:audit-export")
    response = api_client.get(url + "?start_date=2025-07-01&end_date=2025-07-01")
    assert response.status_code == status.HTTP_200_OK
    assert response["Content-Type"] == "text/csv"

    response = api_client.get(url)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    response = api_client.get(
        url + "?start_date=2025-07-01&end_date=2025-07-01&format=pdf"
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_create_appointment_view(api_client, db):
    AuditLog.objects.all().delete()
    url = reverse("audits:create-appointment")
    data = {
        "doctor_id": "DR1003",
        "appointment_date": "2025-07-02T14:30:00Z",
        "patient_id": "PT1005",
    }
    response = api_client.post(url, data, format="json")

    assert response.status_code == status.HTTP_201_CREATED
    assert "appointment_id" in response.data
    assert AuditLog.objects.filter(action=ActionTypes.CREATE).exists()
    audit_log = AuditLog.objects.latest("timestamp")
    assert audit_log.resource_type == "Appointment System"
    assert audit_log.changes == data

    response = api_client.post(url, {}, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST

    client = APIClient()
    response = client.post(url, data, format="json")
    assert response.status_code == status.HTTP_403_FORBIDDEN


# --- URLs Tests ---
@pytest.mark.django_db
def test_audit_urls():
    assert reverse("audits:audit-log-list") == "/api/audits/audit-logs/"
    assert (
        reverse("audits:audit-log-detail", kwargs={"pk": 1})
        == "/api/audits/audit-logs/1/"
    )
    assert reverse("audits:audit-dashboard") == "/api/audits/dashboard/"
    assert reverse("audits:audit-statistics") == "/api/audits/statistics/"
    assert reverse("audits:audit-export") == "/api/audits/export/"

    assert resolve("/api/audits/audit-logs/").view_name == "audits:audit-log-list"
