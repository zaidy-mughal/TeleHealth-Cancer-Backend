from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.doctors.views import (
    SpecializationListCreateView,
    TimeSlotListAPIView,
    DoctorViewSet,
    LicenseInfoListAPIView,
    LicenseInfoCreateAPIView,
    TimeSlotCreateAPIView,
    TimeSlotDeleteAPIView,
    BulkTimeSlotCreateAPIView,
    BulkTimeSlotDeleteAPIView,
    AvailableDoctorDatesAPIView,
)


router = DefaultRouter()
router.register(r"", DoctorViewSet, basename="doctor")

urlpatterns = [
    path(
        "specializations/",
        SpecializationListCreateView.as_view(),
        name="specialization-list-create",
    ),
    path(
        "timeslots/<str:doctor_uuid>",
        TimeSlotListAPIView.as_view(),
        name="time-slot-list-create",
    ),
    path("timeslots/create/", TimeSlotCreateAPIView.as_view(), name="time-slot-create"),
    path(
        "timeslots/bulk-create/",
        BulkTimeSlotCreateAPIView.as_view(),
        name="time-slot-bulk-create",
    ),
    path("timeslots/delete/", TimeSlotDeleteAPIView.as_view(), name="time-slot-delete"),
    path(
        "timeslots/bulk-delete/",
        BulkTimeSlotDeleteAPIView.as_view(),
        name="time-slot-bulk-delete",
    ),
    path("license/", LicenseInfoListAPIView.as_view(), name="license-info-list"),
    path(
        "license/create", LicenseInfoCreateAPIView.as_view(), name="license-info-create"
    ),
    path(
        "available/dates",
        AvailableDoctorDatesAPIView.as_view(),
        name="available_doctor_dates",
    ),
    path("", include(router.urls)),
]
