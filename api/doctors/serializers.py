from rest_framework import serializers
from .models import Doctor, Specialization, TimeSlot
from api.users.serializers import UserSerializer
from api.users.models import User


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
    user = UserSerializer()
    specialization = SpecializationSerializer()

    class Meta:
        model = Doctor
        fields = "__all__"

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

        