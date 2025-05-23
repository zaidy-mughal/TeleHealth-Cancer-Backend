from os import read
from rest_framework import serializers
from django.db import transaction


from api.doctors.models import TimeSlot
from api.doctors.serializers import TimeSlotSerializer
from api.patients.utils.fields import LabelChoiceField
from api.patients.models import Patient
from api.patients.serializers import PatientSerializer
from api.appointments.models import Appointment
from api.appointments.choices import Status
from api.appointments.validators import (
    validate_time_slot,
)


class AppointmentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Appointment model.
    This serializer is used to create appointments.
    It includes the time slot and patient information.
    """

    time_slot_uuid = serializers.UUIDField(write_only=True)
    time_slot = TimeSlotSerializer(read_only=True)
    patient = PatientSerializer(read_only=True)
    status = LabelChoiceField(choices=Status.choices, default=Status.PENDING, read_only=True)
    doctor = serializers.SerializerMethodField(read_only=True)

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
            "id",
            "uuid",
            "doctor",
            "patient",
            "time_slot_uuid",
            "time_slot",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "uuid",
            "doctor",
            "time_slot",
            "status",
            "patient",
            "created_at",
            "updated_at",
        ]

    @transaction.atomic
    def create(self, validated_data):
        try:
            request = self.context["request"]
            patient = Patient.objects.get(user=request.user)
            validated_data["patient"] = patient
            time_slot_uuid = validated_data.pop("time_slot_uuid")
            # mark the time slot as booked
            time_slot = TimeSlot.objects.get(uuid=time_slot_uuid)
            validated_data["time_slot"] = time_slot
            time_slot.is_booked = True
            time_slot.save()
            return super().create(validated_data)

        except Patient.DoesNotExist:
            raise serializers.ValidationError("Patient profile not found for this user")

        except Exception as e:
            raise serializers.ValidationError(f"Error creating appointment: {str(e)}")
