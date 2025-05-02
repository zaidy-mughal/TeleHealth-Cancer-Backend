from django.db import models
from api.base_models import BaseModel
from api.doctors.models import Doctor, TimeSlot
from api.patients.models import Patient
from api.appointments.choices import Status


class Appointments(BaseModel):
    """
    Appointments model to store appointment information.
    This model includes the doctor and patient associated with the appointment.
    """

    doctor = models.ForeignKey(
        Doctor, on_delete=models.CASCADE, related_name="appointments"
    )
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="appointments"
    )
    time_slot = models.OneToOneField(
        TimeSlot, on_delete=models.DO_NOTHING, related_name="appointments"
    )
    status = models.IntegerField(choices=Status.choices)

    def __str__(self):
        return f"{self.doctor.user.get_full_name()} - {self.patient.user.get_full_name()} - {self.time_slot.start_time} - {self.time_slot.end_time}"
