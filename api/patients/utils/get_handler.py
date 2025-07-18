import logging

from rest_framework import serializers

from api.appointments.models import Appointment
from api.patients.models import PatientMedicalRecord

logger = logging.getLogger(__name__)


def get_medical_record_data(context, field_name, item_serializer_class):
    request = context.get("request")
    appointment_uuid = context.get("appointment_uuid", None)

    if not field_name or not item_serializer_class:
        raise ValueError("Both 'field_name' and 'item_serializer_class' are required")

    try:
        patient = request.user.patient

        if appointment_uuid:
            appointment = Appointment.objects.get(uuid=appointment_uuid)
            record_data = getattr(appointment.medical_record, field_name, [])
        else:
            main_record = patient.medical_records.get(is_main_record=True)
            record_data = getattr(main_record, field_name, [])

        return {
            field_name: item_serializer_class(
                record_data or [],
                many=True,
            ).data
        }

    except Appointment.DoesNotExist:
        raise serializers.ValidationError(
            {"detail": "Appointment with the given UUID does not exist."}
        )
    except PatientMedicalRecord.DoesNotExist:
        raise serializers.ValidationError(
            {"detail": "Patient medical record does not exist for appointment."}
        )
    except Exception:
        logger.exception("Unexpected error in get_medical_record_data")
        raise serializers.ValidationError(
            {"detail": f"Failed to get medical record for field '{field_name}'"}
        )
