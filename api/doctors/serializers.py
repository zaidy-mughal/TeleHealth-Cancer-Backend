from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.doctors.choices import StateChoices
from api.doctors.models import (
    Doctor,
    Specialization,
    TimeSlot,
    LicenseInfo,
    Service,
    DoctorService,
)
from api.doctors.validators import (
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

    specialization = SpecializationSerializer(read_only=True)

    time_slots = serializers.SerializerMethodField()

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
            "time_slots",
            "date_of_birth",
            "address",
            "npi_number",
        ]
        read_only_fields = [
            "id",
            "uuid",
            "first_name",
            "last_name",
            "time_slots",
            "created_at",
            "updated_at",
        ]


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


class Services(serializers.ModelSerializer):
    """
    Serializer for Doctor Services
    """

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
