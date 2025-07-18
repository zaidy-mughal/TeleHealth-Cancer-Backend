import logging
from rest_framework import serializers
from api.patients.models import PatientMedicalRecord
from api.patients.validators import validate_medical_record_field
from api.appointments.models import Appointment

logger = logging.getLogger(__name__)


def update_json_field(context, field_name, validated_data):
    """
    Update a JSON field in the user's medical record.
    """
    try:
        patient = context['request'].user.patient
        appointment_uuid = context.get("appointment_uuid", None)
        validate_medical_record_field(field_name)

        if not isinstance(validated_data, dict):
            raise serializers.ValidationError(
                {"detail": f"{field_name} must be a dictionary."}
            )

        if field_name == "iodine_allergy":
            data = validated_data
        else:
            data = validated_data.get(field_name, None)
            if data is None:
                raise serializers.ValidationError(
                    {f"detail": f"{field_name} is required for appointment updates."}
                )

        if not appointment_uuid:
            medical_record = PatientMedicalRecord.objects.get(
                patient=patient, is_main_record=True
            )

        else:
            appointment = Appointment.objects.get(
                uuid=appointment_uuid, medical_record__patient=patient
            )
            medical_record = appointment.medical_record

        setattr(medical_record, field_name, data)
        medical_record.save(update_fields=[f"{field_name}"])
        return medical_record

    except PatientMedicalRecord.DoesNotExist:
        logger.error(
            "PatientMedicalRecord does not exist for appointment."
        )
        raise serializers.ValidationError(
            {"detail": "Patient medical record does not exist for appointment."}
        )
