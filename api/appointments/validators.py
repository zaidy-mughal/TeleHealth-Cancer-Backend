from rest_framework import serializers
from api.appointments.models import Appointment
from api.doctors.models import TimeSlot


def validate_time_slot(self, timeslot_uuid):
    if Appointment.objects.filter(time_slot=timeslot_uuid).exists():
        raise serializers.ValidationError("This time slot is already booked.")

    elif not TimeSlot.objects.filter(uuid=timeslot_uuid).exists():
        raise serializers.ValidationError("This time slot does not exist.")

    elif not TimeSlot.objects.filter(uuid=timeslot_uuid, is_booked=False).exists():
        raise serializers.ValidationError("This time slot is not available.")
