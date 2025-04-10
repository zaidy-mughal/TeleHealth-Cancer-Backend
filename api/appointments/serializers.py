from rest_framework import serializers
from .models import Appointments
from api.doctors.models import Doctor, TimeSlot
from api.patients.models import Patient
from api.patients.serializers import PatientSerializer
from .validators import (
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
        validate_doctor_time_slot(doctor, appointment_time)
        validate_appointment_conflicts(doctor, appointment_date, appointment_time, instance=self.instance)

        return data