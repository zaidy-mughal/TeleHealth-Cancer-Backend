import logging
from rest_framework import serializers
from api.patients.models import PatientMedicalRecord

logger = logging.getLogger(__name__)


def update_json_field(patient, field_name, validated_data):
    """
    Update a JSON field in the user's medical record.
    """
    try:
        field_names = [
            "iodine_allergy",
            "allergies",
            "medications",
            "medical_histories",
            "surgical_histories",
            "cancer_history",
            "addiction_history",
        ]
        if field_name not in field_names:
            raise serializers.ValidationError(
                {
                    "detail": f"Invalid field name: {field_name}. Must be one of {field_names}."
                }
            )
        medical_record = PatientMedicalRecord.objects.get(patient=patient).first()
        setattr(medical_record, field_name, validated_data)
        medical_record.save(update_fields=[f"{field_name}"])
        return medical_record

    except PatientMedicalRecord.DoesNotExist:
        raise serializers.ValidationError(
            {"detail": "Patient medical record does not exist."}
        )
