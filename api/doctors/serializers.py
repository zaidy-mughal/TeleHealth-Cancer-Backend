from rest_framework import serializers
from .models import Doctor, Specialization, TimeSlot, LicenseInfo
from api.users.serializers import UserDetailsSerializer


class SpecializationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Specialization model.
    """

    class Meta:
        model = Specialization
        fields = "__all__"


class DoctorSerializer(serializers.ModelSerializer):
    """
    Serializer for the Doctor model.
    """
    user = UserDetailsSerializer()
    specialization = SpecializationSerializer()

    class Meta:
        model = Doctor
        fields = "__all__"

# will add validations to timeslot in doctor
class TimeSlotSerializer(serializers.ModelSerializer):
    """
    Serializer for the TimeSlot model.
    """
    doctor = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all()
    )

    class Meta:
        model = TimeSlot
        fields = "__all__"


class LicenseInfoSerializer(serializers.ModelSerializer):
    """
    Serializer for the LicenseInfo model.
    """
    doctor = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all()
    )

    class Meta:
        model = LicenseInfo
        fields = "__all__"
