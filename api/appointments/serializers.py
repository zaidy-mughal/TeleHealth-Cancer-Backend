from rest_framework import serializers
from django.db import transaction

from api.appointments.models import Appointments
from api.doctors.models import Doctor, TimeSlot
from api.doctors.serializers import TimeSlotSerializer
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
    time_slot = serializers.PrimaryKeyRelatedField(queryset=TimeSlot.objects.all())
    patient = PatientSerializer()

    class Meta:
        model = Appointments
        fields = [
            "id",
            "uuid",
            "doctor",
            "patient",
            "time_slot",
            "status",
            "created_at",
            "updated_at"
        ]
        read_only_fields = ["id", 'uuid', "created_at", "updated_at", "status"]


    def validate(self, data):
        """
        all validations
        """

        doctor = data.get('doctor')
        time_slot = data.get('time_slot')

        # validate_if_time_slot_is_booked_already
        # validate_if_time_slot_is_of_same_doctor

        # # Use time_slot fields to validate the appointment time

        # validate_future_datetime(appointment_date, appointment_time)
        # validate_doctor_time_slot(doctor, appointment_time)
        # validate_appointment_conflicts(doctor, appointment_date, appointment_time, instance=self.instance)

        return data

    @transaction.atomic
    def create(self, validated_data):
        """
        Create a new appointment and update patient details.
        """
        patient_data = validated_data.pop('patient')
        time_slot = validated_data.pop('time_slot')

        # Get the user from the request context
        user = self.context['request'].user

        try:
            patient_instance = Patient.objects.get(user=user)

            # Update patient instance with provided data
            patient_serializer = PatientSerializer(
                instance=patient_instance,
                data=patient_data,
                partial=True
            )

            # Validate and save patient data
            if patient_serializer.is_valid(raise_exception=True):
                updated_patient = patient_serializer.save()
            
            # Create appointment with the updated patient
            appointment = Appointments.objects.create(
                doctor=validated_data.get('doctor'),
                patient=updated_patient,
                time_slot=time_slot,
            )
            appointment.time_slot.is_booked = True
            appointment.time_slot.save()
            appointment.save()

        except Patient.DoesNotExist:
            raise serializers.ValidationError("Patient profile not found for this user")
        
        except Exception as e:
            raise serializers.ValidationError(f"Error creating appointment: {str(e)}")

        return appointment