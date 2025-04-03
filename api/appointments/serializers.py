from rest_framework import serializers
from django.utils import timezone
from api.patients.serializers import PatientSerializer
from .models import Appointment, Doctor, DoctorAvailability, AvailabilityException


class DoctorSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Doctor
        fields = ['id', 'first_name', 'last_name', 'email', 'specialty', 'bio']


class DoctorAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = DoctorAvailability
        fields = '__all__'


class AvailabilityExceptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AvailabilityException
        fields = '__all__'


class AppointmentSerializer(serializers.ModelSerializer):
    patient_details = PatientSerializer(source='patient', read_only=True)
    doctor_details = DoctorSerializer(source='doctor', read_only=True)

    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'patient_details', 'doctor_details']

    def validate(self, data):
        """
        Validate appointment times using the combined date and time.
        """
        # Only validate if both date and time are present in the data.
        if 'date' in data and 'time' in data:
            appointment_datetime = timezone.make_aware(
                timezone.datetime.combine(data['date'], data['time'])
            )
            if appointment_datetime <= timezone.now():
                raise serializers.ValidationError("Cannot schedule appointments in the past")
        return data


class AppointmentBookingSerializer(serializers.Serializer):
    doctor_id = serializers.IntegerField()
    date = serializers.DateField()
    time = serializers.TimeField()
    reason_for_visit = serializers.CharField(required=False, allow_blank=True)

    # Include payment-related fields
    payment_method = serializers.CharField(max_length=100)
    payment_token = serializers.CharField(max_length=255)

    def validate(self, data):
        """
        Validate appointment booking data.
        """
        # Get doctor
        try:
            doctor = Doctor.objects.get(id=data['doctor_id'])
        except Doctor.DoesNotExist:
            raise serializers.ValidationError("Doctor not found")

        # Check that the combined appointment date and time is in the future.
        appointment_datetime = timezone.make_aware(
            timezone.datetime.combine(data['date'], data['time'])
        )
        if appointment_datetime <= timezone.now():
            raise serializers.ValidationError("Cannot schedule appointments in the past")

        return data