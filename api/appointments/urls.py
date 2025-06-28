from django.urls import path
from api.appointments.views import (
    PatientAppointmentListView,
    AppointmentCreateView,
    AppointmentDetailView,
    DoctorAppointmentListView,
    IodineAllergyAppointmentUpdateView,
    AllergyBulkAppointmentUpdateView,
    MedicationBulkAppointmentUpdateView,
    MedicalHistoryBulkAppointmentUpdateView,
    SurgicalHistoryBulkAppointmentUpdateView,
    CareProviderBulkAppointmentUpdateView,
    AddictionHistoryBulkAppointmentUpdateView,
    CancerHistoryBulkAppointmentUpdateView,
)


urlpatterns = [
    path(
        "patient/",
        PatientAppointmentListView.as_view(),
        name="patient-appointments-list",
    ),
    path("<uuid:uuid>/", AppointmentDetailView.as_view(), name="appointment-detail"),
    path(
        "doctor/", DoctorAppointmentListView.as_view(), name="doctor-appointments-list"
    ),
    path("create/", AppointmentCreateView.as_view(), name="appointment-create"),
    path(
        "iodine-allergy/",
        IodineAllergyAppointmentUpdateView.as_view(),
        name="iodine-allergy-update",
    ),
    path(
        "allergies/",
        AllergyBulkAppointmentUpdateView.as_view(),
        name="allergy-bulk-update",
    ),
    path(
        "medications/",
        MedicationBulkAppointmentUpdateView.as_view(),
        name="medication-bulk-update",
    ),
    path(
        "medical-history/",
        MedicalHistoryBulkAppointmentUpdateView.as_view(),
        name="medical-history-bulk-update",
    ),
    path(
        "surgical-history/",
        SurgicalHistoryBulkAppointmentUpdateView.as_view(),
        name="surgical-history-bulk-update",
    ),
    path(
        "care-providers/",
        CareProviderBulkAppointmentUpdateView.as_view(),
        name="care-provider-bulk-update",
    ),
    path(
        "addiction-history/",
        AddictionHistoryBulkAppointmentUpdateView.as_view(),
        name="addiction-history-bulk-update",
    ),
    path(
        "cancer-history/",
        CancerHistoryBulkAppointmentUpdateView.as_view(),
        name="cancer-history-bulk-update",
    ),
]
