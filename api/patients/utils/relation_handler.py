import logging
from django.db import transaction
from rest_framework.exceptions import APIException

from api.patients.models import (
    CareProvider,
    PatientCareProvider,
    CancerHistory,
    CancerType,
    TreatmentRecieved,
    AddictionHistory,
)

logger = logging.getLogger(__name__)


class PatientRelationHandlerMixin:
    relation_model = None
    target_model = None
    related_field_name = ""
    data_key = ""

    @transaction.atomic
    def handle_relation(self, validated_data, clear_existing=False):
        try:
            items_data = validated_data.get(self.data_key, [])
            patient = self.context["request"].user.patient

            if clear_existing:
                self.relation_model.objects.filter(patient=patient).delete()

            self._create_relation_objects(items_data, patient)

            message = (
                "Updated successfully" if clear_existing else "Created successfully"
            )
            return {"message": message}

        except Exception as e:
            logger.error(f"Error in handle_relation: {str(e)}")
            raise APIException(f"Failed to process {self.data_key}: {str(e)}")

    def _create_relation_objects(self, items_data, patient):
        for item_data in items_data:
            item_obj, _ = self.target_model.objects.get_or_create(
                name=item_data["name"]
            )
            self.relation_model.objects.get_or_create(
                patient=patient, **{self.related_field_name: item_obj}
            )


@transaction.atomic
def handle_care_provider(validated_data, clear_existing=False):
    try:
        care_providers_data = validated_data.get("care_providers", [])
        patient = validated_data.get("patient")

        if not care_providers_data:
            return {"message": "No care providers data provided."}

        # Clear existing records
        PatientCareProvider.objects.filter(patient=patient).delete()

        # Create new records
        create_care_provider_relations(care_providers_data, patient)

        message = "Updated successfully" if clear_existing else "Created successfully"
        return {"message": message}

    except Exception as e:
        logger.error(f"Error in handle_care_provider: {str(e)}")
        raise APIException(f"Failed to process care providers: {str(e)}")


def create_care_provider_relations(care_providers_data, patient):
    for provider_data in care_providers_data:
        care_provider, _ = CareProvider.objects.get_or_create(
            name=provider_data["name"],
            contact_number=provider_data["contact_number"],
            type=provider_data["type"],
        )
        PatientCareProvider.objects.create(patient=patient, care_provider=care_provider)


@transaction.atomic
def handle_cancer_history_list(validated_data, clear_existing=False):
    """Handle creation/updating of multiple cancer history records."""
    try:
        cancer_history_data = validated_data.get("cancer_histories", [])
        patient = validated_data.get("patient")

        if clear_existing:
            CancerHistory.objects.filter(patient=patient).delete()

        create_cancer_history_records(cancer_history_data, patient)

        return {"message": "Cancer history updated successfully"}

    except Exception as e:
        logger.error(f"Error in handle_cancer_history_list: {str(e)}")
        raise APIException(f"Failed to process cancer history: {str(e)}")


def create_cancer_history_records(history_data_list, patient):
    for history_data in history_data_list:
        # Extract nested data
        cancer_type_data = history_data.pop("cancer_type")
        treatment_data = history_data.pop("treatment_received", [])

        # Create cancer type and history
        cancer_type, _ = CancerType.objects.get_or_create(**cancer_type_data)
        instance = CancerHistory.objects.create(
            patient=patient,
            cancer_type=cancer_type,
            year_of_diagnosis=history_data["year_of_diagnosis"],
        )

        for treatment in treatment_data:
            TreatmentRecieved.objects.create(
                cancer_history=instance, name=treatment["name"]
            )


@transaction.atomic
def handle_addiction_history(validated_data, clear_existing=False):
    try:
        addiction_history_data = validated_data.get("addiction_history", [])
        patient = validated_data.get("patient")

        if clear_existing:
            AddictionHistory.objects.filter(patient=patient).delete()

        create_addiction_records(addiction_history_data, patient)

        message = "Updated successfully" if clear_existing else "Created successfully"
        return {"message": message}

    except Exception as e:
        logger.error(f"Error in handle_addiction_history: {str(e)}")
        raise APIException(f"Failed to process addiction history: {str(e)}")


def create_addiction_records(addiction_data_list, patient):
    for addiction_data in addiction_data_list:
        AddictionHistory.objects.create(
            patient=patient,
            addiction_type=addiction_data["addiction_type"],
            total_years=addiction_data["total_years"],
        )
