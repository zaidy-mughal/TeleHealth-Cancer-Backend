from rest_framework import serializers
from .models import Appointments
from api.doctors.models import TimeSlot
from django.utils import timezone


def validate_doctor_time_slot(doctor, appointment_time):
    """
    Check if the requested time falls within doctor's available time slots.
    """
    time_slots = TimeSlot.objects.filter(doctor=doctor)
    for slot in time_slots:
        if slot.start_time <= appointment_time <= slot.end_time:
            return True
    raise serializers.ValidationError("Doctor is not available at the requested time")


def validate_appointment_conflicts(doctor, appointment_date, appointment_time, instance=None):
    """
    Check for any conflicting appointments at the requested time.
    """
    existing_appointments = Appointments.objects.filter(
        doctor=doctor,
        appointment_date=appointment_date,
        appointment_time=appointment_time
    )
    
    if instance:
        existing_appointments = existing_appointments.exclude(uuid=instance.uuid)
        
    if existing_appointments.exists():
        raise serializers.ValidationError("Doctor already has an appointment at this time")


def validate_future_datetime(appointment_date, appointment_time):
    """
    Ensure appointment is scheduled for a future date and time.
    """
    appointment_datetime = timezone.make_aware(
        timezone.datetime.combine(appointment_date, appointment_time)
    )
    
    if appointment_datetime <= timezone.now():
        raise serializers.ValidationError("Appointment must be scheduled for a future date and time")