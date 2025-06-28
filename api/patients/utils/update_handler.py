import logging
from rest_framework import serializers
from api.patients.models import PatientMedicalRecord
from api.appointments.models import Appointment

logger = logging.getLogger(__name__)


def update_json_field(patient, field_name, validated_data, is_appointment_update):
    """
    Update a JSON field in the user's medical record.
    """
    try:
        # TODO add validations in the validator.py
        field_names = [
            "iodine_allergy",
            "allergies",
            "medications",
            "medical_histories",
            "surgical_histories",
            "cancer_history",
            "addiction_history",
            "care_providers",
        ]
        if field_name not in field_names:
            raise serializers.ValidationError(
                {
                    "detail": f"Invalid field name: {field_name}. Must be one of {field_names}."
                }
            )

        if field_name == "iodine_allergy":
            data = validated_data
        else:
            data = validated_data.get(field_name, None)
            if data is None:
                raise serializers.ValidationError(
                    {f"detail": f"{field_name} is required for appointment updates."}
                )

        appointment_uuid = validated_data.pop("appointment_uuid", None)

        if not isinstance(validated_data, dict):
            raise serializers.ValidationError(
                {"detail": f"{field_name} must be a dictionary."}
            )

        if not is_appointment_update:
            medical_record = PatientMedicalRecord.objects.get(
                patient=patient, is_main_record=True
            )

        else:
            if not appointment_uuid:
                raise serializers.ValidationError(
                    {"detail": "appointment_uuid is required for appointment updates."}
                )
            appointment = Appointment.objects.get(
                uuid=appointment_uuid, medical_record__patient=patient
            )
            if not appointment:
                raise serializers.ValidationError(
                    {"detail": "Appointment with the given UUID does not exist."}
                )
            medical_record = appointment.medical_record
            if not medical_record:
                raise serializers.ValidationError(
                    {"detail": "Medical record does not exist for the appointment."}
                )

        setattr(medical_record, field_name, data)

        medical_record.save(update_fields=[f"{field_name}"])
        return medical_record

    except PatientMedicalRecord.DoesNotExist:
        logger.error(
            f"PatientMedicalRecord does not exist for appointment {appointment_uuid}"
        )
        raise serializers.ValidationError(
            {"detail": "Patient medical record does not exist for appointment."}
        )
