from django.urls import path, include

from .views import (
    IodineAllergyViewSet,
    PatientAllergyViewSet,
    PatientMedicationViewSet,
    PatientMedicalHistoryViewSet,
    PatientSurgicalHistoryViewSet,
    PatientCareProviderViewSet,
    CancerHistoryViewSet,
    PatientAddictionHistoryViewSet,
    PatientRetreiveView,
)


urlpatterns = [
    path(
        "iodine-allergy/create/",
        IodineAllergyViewSet.as_view({"post": "create"}),
    ),
    path(
        "iodine-allergy/update/",
        IodineAllergyViewSet.as_view({"put": "update"}),
    ),
    path(
        "cancer-history/create/",
        CancerHistoryViewSet.as_view({"post": "create"}),
        name="cancer-history-create",
    ),
    path(
        "cancer-history/update/<uuid:uuid>/",
        CancerHistoryViewSet.as_view({"put": "update"}),
        name="cancer-history-update",
    ),
    path(
        "allergies/create/", PatientAllergyViewSet.as_view({"post": "create_allergies"})
    ),
    path(
        "allergies/update/", PatientAllergyViewSet.as_view({"put": "update_allergies"})
    ),
    path(
        "medications/create/",
        PatientMedicationViewSet.as_view({"post": "create_medications"}),
    ),
    path(
        "medications/update/",
        PatientMedicationViewSet.as_view({"put": "update_medications"}),
    ),
    path(
        "medical-history/create/",
        PatientMedicalHistoryViewSet.as_view({"post": "create_medical_history"}),
    ),
    path(
        "medical-history/update/",
        PatientMedicalHistoryViewSet.as_view({"put": "update_medical_history"}),
    ),
    path(
        "surgical-history/create/",
        PatientSurgicalHistoryViewSet.as_view({"post": "create_surgical_history"}),
    ),
    path(
        "surgical-history/update/",
        PatientSurgicalHistoryViewSet.as_view({"put": "update_surgical_history"}),
    ),
    path(
        "care-providers/create/",
        PatientCareProviderViewSet.as_view({"post": "create_care_providers"}),
    ),
    path(
        "care-providers/update/",
        PatientCareProviderViewSet.as_view({"put": "update_care_providers"}),
    ),
    path(
        "addiction-history/create/",
        PatientAddictionHistoryViewSet.as_view({"post": "create_addiction_history"}),
    ),
    path(
        "addiction-history/update/",
        PatientAddictionHistoryViewSet.as_view({"put": "update_addiction_history"}),
    ),
    path("me/", PatientRetreiveView.as_view(), name="patient-retrieve"),
]
