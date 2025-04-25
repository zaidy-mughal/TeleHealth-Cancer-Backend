from rest_framework import serializers
from .models import Appointments
from api.doctors.models import Doctor, TimeSlot
from api.patients.models import Patient
from api.patients.serializers import PatientSerializer
from api.appointments.validators import (
    validate_doctor_time_slot,
    validate_appointment_conflicts,
    validate_future_datetime,
)


class AppointmentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Appointments model.
    This serializer is used to convert Appointment model instances to JSON and vice versa.
    """
    doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all())
    patient = PatientSerializer()

    class Meta:
        model = Appointments
        fields = [
            "uuid",
            "doctor",
            "patient",
            "appointment_date",
            "appointment_time",
            "status",
            "created_at",
            "updated_at"
        ]
        read_only_fields = ["uuid", "created_at", "updated_at"]


    def validate(self, data):
        """
        all validations
        """

        doctor = data.get('doctor')
        appointment_date = data.get('appointment_date')
        appointment_time = data.get('appointment_time')

        validate_future_datetime(appointment_date, appointment_time)
        # validate_doctor_time_slot(doctor, appointment_time)
        # validate_appointment_conflicts(doctor, appointment_date, appointment_time, instance=self.instance)

        return data


    def create(self, validated_data):
        """
        Create a new appointment and update patient details.
        """
        patient_data = validated_data.pop('patient')

        # Get the user from the request context
        user = self.context['request'].user

        try:
            patient_instance = Patient.objects.get(user=user)
        except Patient.DoesNotExist:
            raise serializers.ValidationError("Patient profile not found for this user")

        # Update patient instance with provided data
        patient_serializer = PatientSerializer(
            instance=patient_instance,
            data=patient_data,
            partial=True
        )

        # Validate and save patient data
        if patient_serializer.is_valid(raise_exception=True):
            updated_patient = patient_serializer.save()
        else:
            raise serializers.ValidationError(patient_serializer.errors)

        # Create appointment with the updated patient
        appointment = Appointments.objects.create(
            doctor=validated_data.get('doctor'),
            patient=updated_patient,
            appointment_date=validated_data.get('appointment_date'),
            appointment_time=validated_data.get('appointment_time'),
            status=validated_data.get('status', 'SCHEDULED')
        )

        return appointment