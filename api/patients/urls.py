from django.urls import path

from api.patients.views import (
    IodineAllergyUpdateView,
    AllergyBulkUpdateView,
    CancerHistoryBulkUpdateView,
    MedicationBulkUpdateView,
    MedicalHistoryBulkUpdateView,
    SurgicalHistoryBulkUpdateView,
    CareProviderBulkUpdateView,
    AddictionHistoryBulkUpdateView,
    PatientRetreiveView,
)


urlpatterns = [
    path(
        "iodine-allergy/",
        IodineAllergyUpdateView.as_view(),
        name="iodine-allergy-update",
    ),
    path("allergies/", AllergyBulkUpdateView.as_view(), name="allergies-update"),
    path(
        "medications/",
        MedicationBulkUpdateView.as_view(),
        name="medication-update",
    ),
    path(
        "medical-history/",
        MedicalHistoryBulkUpdateView.as_view(),
        name="medical-history-update",
    ),
    path(
        "surgical-history/",
        SurgicalHistoryBulkUpdateView.as_view(),
        name="surgical-history-update",
    ),
    path(
        "care-providers/",
        CareProviderBulkUpdateView.as_view(),
        name="care-provider-update",
    ),
    path(
        "addiction-history/",
        AddictionHistoryBulkUpdateView.as_view(),
        name="addiction-history-update",
    ),
    path(
        "cancer-history/",
        CancerHistoryBulkUpdateView.as_view(),
        name="cancer-history-update",
    ),
    path("me/", PatientRetreiveView.as_view(), name="patient-retrieve"),
]
