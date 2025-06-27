from django.urls import path, include

from .views import (
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
        "iodine-allergy/update/",
        IodineAllergyUpdateView.as_view(),
    ),
    path(
        "cancer-history/update/",
        CancerHistoryBulkUpdateView.as_view(),
        name="cancer-history-update",
    ),
    path("allergies/update/", AllergyBulkUpdateView.as_view()),
    path(
        "medications/update/",
        MedicationBulkUpdateView.as_view(),
    ),
    path(
        "medical-history/update/",
        MedicalHistoryBulkUpdateView.as_view(),
    ),
    path(
        "surgical-history/update/",
        SurgicalHistoryBulkUpdateView.as_view(),
    ),
    path(
        "care-providers/update/",
        CareProviderBulkUpdateView.as_view(),
    ),
    path(
        "addiction-history/update/",
        AddictionHistoryBulkUpdateView.as_view(),
    ),
    path("me/", PatientRetreiveView.as_view(), name="patient-retrieve"),
]
