from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.db import transaction

from api.doctors.choices import Services, StateChoices
from api.doctors.models import (
    Doctor,
    Specialization,
    TimeSlot,
    LicenseInfo,
    Service,
    DoctorService,
)
from api.doctors.validators import (
    validate_bulk_time_slots,
    validate_user_role,
    validate_start_time_lt_end_time,
    future_start_time,
)
from api.patients.utils.fields import LabelChoiceField

User = get_user_model()


class SpecializationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Specialization model.
    """

    class Meta:
        model = Specialization
        fields = ["name"]


# will add validations to timeslot in doctor
class TimeSlotSerializer(serializers.ModelSerializer):
    """
    Serializer for the TimeSlot model.
    """

    def validate(self, attrs):
        """
        Validate timeslots for the doctor.
        """
        validate_start_time_lt_end_time(attrs["start_time"], attrs["end_time"])
        future_start_time(attrs["start_time"])

        return attrs

    class Meta:
        model = TimeSlot
        fields = ["id", "uuid", "start_time", "end_time", "is_booked"]
        read_only_fields = ["id", "uuid", "is_booked"]

    def create(self, validated_data):
        validated_data["doctor"] = self.context["request"].user.doctor
        return super().create(validated_data)


class TimeSlotBulkUpdateSerializer(serializers.Serializer):
    """
    Serializer for bulk updating time slots creating new ones and deleting the slots marked to_delete = true.
    """

    time_slots = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        help_text="List of time slots to create or delete. "
        "Each item can have 'uuid' for deletion, 'start_time' and 'end_time' for creation.",
    )

    def validate_time_slots(self, value):
        validate_bulk_time_slots(value)
        return value

    @transaction.atomic
    def save(self):
        doctor = self.context["request"].user.doctor
        time_slots_data = self.validated_data["time_slots"]

        slots_to_delete = []
        slots_to_create = []

        for slot_data in time_slots_data:
            # appending the slots for deletion
            if slot_data.get("to_delete", False):
                uuid = slot_data.get("uuid")
                if not uuid:
                    raise serializers.ValidationError(
                        "UUID is required for deletion of time slots."
                    )
                slots_to_delete.append(uuid)

            else:
                # Check if the slot already exists OR append to creation
                uuid = slot_data.get("uuid")
                if uuid and self._slot_exists_by_uuid(uuid, doctor):
                    continue
                else:
                    slots_to_create.append(slot_data)

        deleted_count = self._delete_slots(slots_to_delete, doctor)
        created_slots = self._create_slots(slots_to_create, doctor)

        return {
            "doctor": doctor.uuid,
            "doctor_name": f"{doctor.user.first_name} {doctor.user.last_name}",
            "deleted_count": deleted_count,
            "created_slots": created_slots,
        }

    def _slot_exists_by_uuid(self, uuid, doctor):
        try:
            return TimeSlot.objects.filter(uuid=uuid, doctor=doctor).exists()
        except (ValueError, TypeError):
            return False

    def _delete_slots(self, slots_to_delete, doctor):
        if not slots_to_delete:
            return 0

        deleted_count = 0

        for slot in slots_to_delete:
            if isinstance(slot, str):
                deleted_count += TimeSlot.objects.filter(
                    uuid=slot, doctor=doctor
                ).delete()[0]

        return deleted_count

    def _create_slots(self, slots_data, doctor):
        if not slots_data:
            return []

        created_slots = []

        for slot_data in slots_data:
            clean_data = {
                k: v for k, v in slot_data.items() if k in ["start_time", "end_time"]
            }

            slot_serializer = TimeSlotSerializer(data=clean_data, context=self.context)
            slot_serializer.is_valid(raise_exception=True)
            slot_serializer.save()

            created_slots.append(slot_serializer.data)

        return created_slots


class LicenseInfoSerializer(serializers.ModelSerializer):
    """
    Serializer for the LicenseInfo model.
    """

    state = LabelChoiceField(choices=StateChoices.choices)

    class Meta:
        model = LicenseInfo
        fields = ["license_number", "state", "doctor"]
        read_only_fields = ["doctor"]

    def create(self, validated_data):
        validated_data["doctor"] = self.context["request"].user.doctor
        return super().create(validated_data)


class ServiceSerializer(serializers.ModelSerializer):
    name = LabelChoiceField(choices=Services.choices)

    class Meta:
        model = Service
        fields = ["id", "uuid", "name"]
        read_only_fields = ["id", "uuid"]


class DoctorServiceSerializer(serializers.ModelSerializer):
    doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all())
    service = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all())

    class Meta:
        model = DoctorService
        fields = ["doctor", "service"]

    def to_representation(self, instance):
        service_data = ServiceSerializer(instance.service).data
        return {"doctor": instance.doctor.uuid, "service": service_data["name"]}


class DoctorSerializer(serializers.ModelSerializer):
    """
    Serializer for the Doctor model.
    """

    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)

    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    specialization = serializers.PrimaryKeyRelatedField(
        queryset=Specialization.objects.all(),
        write_only=True,
    )

    services = serializers.SerializerMethodField()
    states = serializers.SerializerMethodField()
    specialization = SpecializationSerializer(read_only=True)
    time_slots = serializers.SerializerMethodField()

    def get_services(self, obj):
        services = obj.doctor_services.all()
        serializer = DoctorServiceSerializer(services, many=True)
        print(serializer.data)
        return [item["service"] for item in serializer.data]

    def get_states(self, obj):
        licenses = obj.license_info.all()
        serializer = LicenseInfoSerializer(licenses, many=True)
        return [item["state"] for item in serializer.data]

    def get_time_slots(self, obj):
        return TimeSlotSerializer(obj.time_slots.all(), many=True).data

    def validate_user(self, user):
        return validate_user_role(self, user)

    class Meta:
        model = Doctor
        fields = [
            "id",
            "uuid",
            "user",
            "first_name",
            "last_name",
            "specialization",
            "states",
            "services",
            "date_of_birth",
            "address",
            "npi_number",
            "time_slots",
        ]
        read_only_fields = [
            "id",
            "uuid",
            "first_name",
            "last_name",
            "states",
            "services",
            "time_slots",
            "created_at",
            "updated_at",
        ]
