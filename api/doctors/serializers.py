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
        fields = ["uuid", "start_time", "end_time", "is_booked"]
        read_only_fields = ["uuid", "is_booked"]

    def create(self, validated_data):
        validated_data["doctor"] = self.context["request"].user.doctor
        return super().create(validated_data)


class TimeSlotBulkDeleteSerializer(serializers.Serializer):
    """
    Serializer for bulk deleting timeslots.
    """

    time_slot_uuids = serializers.ListField(child=serializers.UUIDField(), write_only=True)

    def validate_time_slot_uuids(self, value):
        if not value:
            raise serializers.ValidationError("At least one UUID must be provided.")

        doctor = self.context["request"].user.doctor

        # Get existing timeslots for this doctor
        existing_timeslots = TimeSlot.objects.filter(uuid__in=value, doctor=doctor)

        existing_uuids = set(
            str(uuid) for uuid in existing_timeslots.values_list("uuid", flat=True)
        )
        print(existing_uuids, "====")
        provided_uuids = set(str(uuid) for uuid in value)
        print(provided_uuids, "=====")
        # Check for invalid UUIDs
        invalid_uuids = provided_uuids - existing_uuids
        print(invalid_uuids, "++++")
        if invalid_uuids:
            raise serializers.ValidationError(
                f"Some UUIDs are invalid or don't exist: {list(invalid_uuids)}"
            )

        return value

    def delete_timeslots(self):
        """
        Delete the validated timeslots.
        """
        try:
            uuids = self.validated_data["time_slot_uuids"]
            doctor = self.context["request"].user.doctor

            deleted_count, _ = TimeSlot.objects.filter(
                uuid__in=uuids, doctor=doctor
            ).delete()

            return deleted_count
        except Exception as e:
            raise serializers.ValidationError(f"Error deleting timeslots: {str(e)}")


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
