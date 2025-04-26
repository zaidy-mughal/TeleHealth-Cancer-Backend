from django.db import models
from api.base_models import TimeStampMixin
from api.doctors.models import Doctor
from api.patients.models import Patient
from api.appointments.choices import Status
import uuid


class Appointments(models.Model):
    """
    Appointments model to store appointment information.
    This model includes the doctor and patient associated with the appointment.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Status(models.IntegerChoices):
        PENDING = 0, "Pending"
        CONFIRMED = 1, "Confirmed"
        CANCELLED = 2, "Cancelled"

    doctor = models.ForeignKey(
        Doctor, on_delete=models.CASCADE, related_name="appointments"
    )
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="appointments"
    )
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status = models.IntegerField(choices=Status.choices)

    def __str__(self):
        return f"{self.doctor.user.get_full_name()} - {self.patient.user.get_full_name()} - {self.appointment_date} {self.appointment_time}"
