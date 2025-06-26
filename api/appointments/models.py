from django.db import models
from api.base_models import BaseModel
from api.doctors.choices import Services
from api.appointments.choices import Status


class Appointment(BaseModel):
    """
    Appointments model to store appointment information.
    This model linked with the timeslot and patient record associated with the appointment.
    Patient can be get from the patient record
    It also had follow up appointment, which is linked with it self(Unary relation).
    We can get doctor information from the timeslot.
    """

    time_slot = models.OneToOneField(
        "doctors.TimeSlot",
        on_delete=models.RESTRICT,
        related_name="appointments",
        null=True,
        blank=True,
    )
    follow_up_of = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="follow_up_appointments",
        null=True,
        blank=True,
    )
    status = models.IntegerField(choices=Status.choices, db_default=Status.PENDING)
    appointment_type = models.IntegerField(
        choices=Services.choices,
    )
    medical_record = models.OneToOneField(
        "patients.PatientMedicalRecord",
        on_delete=models.RESTRICT,
        related_name="appointment",
    )

    def __str__(self):
        return f"{self.time_slot.doctor.user.get_full_name()} - {self.medical_record.patient.user.get_full_name()} - {self.time_slot.start_time} - {self.time_slot.end_time}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"
        db_table = "appointment"
