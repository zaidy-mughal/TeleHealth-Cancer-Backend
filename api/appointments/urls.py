from django.urls import path
from api.appointments.views import (
    PatientAppointmentListView,
    AppointmentCreateView,
    AppointmentDetailView,
    DoctorAppointmentListView,
    IodineAllergyAppointmentUpdateRetrieveView,
    AllergyBulkAppointmentUpdateRetrieveView,
    MedicationBulkAppointmentUpdateRetrieveView,
    MedicalHistoryBulkAppointmentUpdateRetrieveView,
    SurgicalHistoryBulkAppointmentUpdateRetrieveView,
    CareProviderBulkAppointmentUpdateRetrieveView,
    AddictionHistoryBulkAppointmentUpdateRetrieveView,
    CancerHistoryBulkAppointmentUpdateRetrieveView,
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
        "<uuid:uuid>/iodine-allergy/",
        IodineAllergyAppointmentUpdateRetrieveView.as_view(),
        name="iodine-allergy-update",
    ),
    path(
        "<uuid:uuid>/allergies/",
        AllergyBulkAppointmentUpdateRetrieveView.as_view(),
        name="allergy-bulk-update",
    ),
    path(
        "<uuid:uuid>/medications/",
        MedicationBulkAppointmentUpdateRetrieveView.as_view(),
        name="medication-bulk-update",
    ),
    path(
        "<uuid:uuid>/medical-history/",
        MedicalHistoryBulkAppointmentUpdateRetrieveView.as_view(),
        name="medical-history-bulk-update",
    ),
    path(
        "<uuid:uuid>/surgical-history/",
        SurgicalHistoryBulkAppointmentUpdateRetrieveView.as_view(),
        name="surgical-history-bulk-update",
    ),
    path(
        "<uuid:uuid>/care-providers/",
        CareProviderBulkAppointmentUpdateRetrieveView.as_view(),
        name="care-provider-bulk-update",
    ),
    path(
        "<uuid:uuid>/addiction-history/",
        AddictionHistoryBulkAppointmentUpdateRetrieveView.as_view(),
        name="addiction-history-bulk-update",
    ),
    path(
        "<uuid:uuid>/cancer-history/",
        CancerHistoryBulkAppointmentUpdateRetrieveView.as_view(),
        name="cancer-history-bulk-update",
    ),
]
