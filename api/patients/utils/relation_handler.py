from django.db import transaction

from api.patients.models import (
    Allergy,
    PatientAllergy,
    Medication,
    PatientMedication,
    MedicalHistory,
    PatientMedicalHistory,
    SurgicalHistory,
    PatientSurgicalHistory,
    CareProvider,
    PatientCareProvider,
    CancerHistory,
    CancerType,
    TreatmentRecieved,
    AddictionHistory,
)

# 975fe322-801c-4024-9fb5-a578c970dc6e

class PatientRelationHandlerMixin:
    relation_model = None
    target_model = None
    related_field_name = ""
    data_key = ""

    @transaction.atomic
    def handle_relation(self, validated_data, clear_existing=False):
        items_data = validated_data.get(self.data_key, [])
        patient = self.context["request"].user.patient

        if clear_existing:
            self.relation_model.objects.filter(patient=patient).delete()

        for item_data in items_data:
            item_obj, _ = self.target_model.objects.get_or_create(
                name=item_data["name"]
            )
            self.relation_model.objects.get_or_create(
                patient=patient, **{self.related_field_name: item_obj}
            )

        return {
            "message": (
                "Updated successfully" if clear_existing else "Created successfully"
            )
        }


# Handler for Care Providers
@transaction.atomic
def handle_care_provider(validated_data, clear_existing=False):
    care_providers_data = validated_data.get("care_providers", [])
    patient = validated_data.get("patient")

    if care_providers_data:
        PatientCareProvider.objects.filter(patient=patient).delete()

        for care_provider_data in care_providers_data:
            care_provider, _ = CareProvider.objects.get_or_create(
                name=care_provider_data["name"],
                contact_number=care_provider_data["contact_number"],
                type=care_provider_data["type"],
            )
            PatientCareProvider.objects.create(
                patient=patient, care_provider=care_provider
            )
        
        return {
            "message": "Updated successfully" if clear_existing else "Created successfully"
        }
    else:
        return {
            "message": "No care providers data provided."
        }


# this will handle one to many relation of cancer history
@transaction.atomic
def handle_cancer_history(validated_data, instance=None):
    cancer_type_data = validated_data.pop("cancer_type")
    treatment_data = validated_data.pop("treatment_received", [])
    patient = validated_data.get("patient")
    cancer_type, _ = CancerType.objects.get_or_create(**cancer_type_data)

    if instance is None:
        instance = CancerHistory.objects.create(
            patient=patient,
            cancer_type=cancer_type,
            year_of_diagnosis=validated_data["year_of_diagnosis"],
        )
    else:
        instance.cancer_type = cancer_type
        instance.year_of_diagnosis = validated_data["year_of_diagnosis"]
        instance.save()
        instance.treatment_received.all().delete()

    for treatment in treatment_data:
        TreatmentRecieved.objects.create(
            cancer_history=instance, name=treatment["name"]
        )

    return instance


# this will handle one to many relation of addiction history
@transaction.atomic
def handle_addiction_history(validated_data, clear_existing=False):
    addiction_history_data = validated_data.get("addiction_history", [])
    patient = validated_data.get("patient")

    if clear_existing:
        AddictionHistory.objects.filter(patient=patient).delete()

    for addiction_data in addiction_history_data:
        AddictionHistory.objects.create(
            patient=patient,
            addiction_type=addiction_data["addiction_type"],
            total_years=addiction_data["total_years"],
        )

    return {
        "message": "Updated successfully" if clear_existing else "Created successfully"
    }
