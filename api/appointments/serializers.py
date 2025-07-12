from rest_framework import serializers
from django.db import transaction


from api.doctors.models import TimeSlot
from api.doctors.choices import Services
from api.doctors.serializers import TimeSlotSerializer
from api.patients.utils.fields import LabelChoiceField
from api.patients.models import Patient
from api.patients.serializers import PatientMedicalRecordSerializer
from api.appointments.models import Appointment
from api.appointments.choices import Status
from api.appointments.validators import (
    validate_time_slot,
)
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class AppointmentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Appointment model.
    This serializer is used to create appointments.
    It includes limited information.
    """

    time_slot_uuid = serializers.UUIDField(write_only=True)
    time_slot = TimeSlotSerializer(read_only=True)
    status = LabelChoiceField(
        choices=Status.choices, default=Status.PENDING, read_only=True
    )
    doctor = serializers.SerializerMethodField(read_only=True)
    appointment_type = LabelChoiceField(choices=Services.choices)

    def get_doctor(self, obj):
        if obj.time_slot:
            return {
                "uuid": obj.time_slot.doctor.uuid,
                "name": obj.time_slot.doctor.user.get_full_name(),
            }
        return None

    def validate(self, data):
        time_slot_uuid = data.get("time_slot_uuid")
        validate_time_slot(self, time_slot_uuid)

        return data

    class Meta:
        model = Appointment
        fields = [
            "uuid",
            "doctor",
            "time_slot_uuid",
            "time_slot",
            "appointment_type",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "uuid",
            "doctor",
            "time_slot",
            "status",
            "appointment_type",
            "created_at",
            "updated_at",
        ]

    @transaction.atomic
    def create(self, validated_data):
        try:
            request = self.context["request"]
            patient = Patient.objects.get(user=request.user)

            medical_record = patient.medical_records.create(is_main_record=False)
            validated_data["medical_record"] = medical_record

            time_slot_uuid = validated_data.pop("time_slot_uuid")
            time_slot = TimeSlot.objects.get(uuid=time_slot_uuid)
            validated_data["time_slot"] = time_slot
            time_slot.is_booked = True
            time_slot.save()

            return super().create(validated_data)

        except Patient.DoesNotExist:
            raise serializers.ValidationError("Patient profile not found for this user")

        except Exception as e:
            logger.exception("Unexpected error")
            raise serializers.ValidationError("Error creating appointment")


class AppointmentDetailSerializer(AppointmentSerializer):
    """
    Serializer for the Appointment model with detailed information.
    This serializer is used to retrieve appointment details.
    It includes the time slot and patient information.
    """

    medical_record = PatientMedicalRecordSerializer(read_only=True)

    class Meta(AppointmentSerializer.Meta):
        fields = AppointmentSerializer.Meta.fields + ["medical_record"]
        read_only_fields = AppointmentSerializer.Meta.read_only_fields + [
            "medical_record"
        ]


class DoctorAppointmentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Appointment model for doctors.
    This serializer is used to retrieve appointments for a doctor.
    It includes the time slot and patient information.
    """

    time_slot = TimeSlotSerializer(read_only=True)
    patient = serializers.SerializerMethodField(read_only=True)
    doctor = serializers.SerializerMethodField(read_only=True)
    status = serializers.SerializerMethodField(read_only=True)
    appointment_type = LabelChoiceField(choices=Services.choices, read_only=True)

    def get_status(self, obj):
        return obj.get_status_display()

    def get_doctor(self, obj):
        if obj.time_slot:
            return {
                "doctor": obj.time_slot.doctor.user.get_full_name(),
            }
        return None

    def get_patient(self, obj):
        if obj.medical_record.patient:
            return {
                "first_name": obj.medical_record.patient.user.first_name,
                "middle_name": obj.medical_record.patient.user.middle_name,
                "last_name": obj.medical_record.patient.user.last_name,
                "state": obj.medical_record.patient.state,
                "gender": obj.medical_record.patient.get_gender_display(),
            }
        return None

    class Meta:
        model = Appointment
        fields = [
            "uuid",
            "time_slot",
            "doctor",
            "patient",
            "status",
            "appointment_type",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "uuid",
            "time_slot",
            "patient",
            "doctor",
            "appointment_type",
            "status",
            "created_at",
            "updated_at",
        ]


# checking deployment comment
