from django.db import models
from api.base_models import BaseModel
from api.doctors.models import TimeSlot
from api.patients.models import Patient
from api.appointments.choices import Status


class Appointment(BaseModel):
    """
    Appointments model to store appointment information.
    This model linked with the timeslot and patient associated with the appointment.
    We can get doctor information from the timeslot.
    """

    patient = models.ForeignKey(
        Patient, on_delete=models.RESTRICT, related_name="appointments"
    )
    time_slot = models.OneToOneField(
        TimeSlot, on_delete=models.RESTRICT, related_name="appointments", null=True, blank=True
    )
    status = models.IntegerField(choices=Status.choices, db_default=Status.PENDING)


    def __str__(self):
        return f"{self.time_slot.doctor.user.get_full_name()} - {self.patient.user.get_full_name()} - {self.time_slot.start_time} - {self.time_slot.end_time}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"
        db_table = "appointment"
        indexes = [
            models.Index(fields=["patient"]),
        ]
