from django.db import models
from api.base_models import TimeStampMixin
from api.doctors.models import Doctor
from api.patients.models import Patient
import uuid


class Appointments(TimeStampMixin):
    """
    Appointments model to store appointment information.
    This model includes the doctor and patient associated with the appointment.
    """
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        CONFIRMED = "CONFIRMED", "Confirmed"
        CANCELLED = "CANCELLED", "Cancelled"

    id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False, primary_key=True)

    doctor = models.ForeignKey(
        Doctor, on_delete=models.CASCADE, related_name="appointments"
    )
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="appointments"
    )
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status = models.CharField(max_length=20, choices=Status.choices)

    def __str__(self):
        return f"{self.doctor.user.get_full_name()} - {self.patient.user.get_full_name()} - {self.appointment_date} {self.appointment_time}"
