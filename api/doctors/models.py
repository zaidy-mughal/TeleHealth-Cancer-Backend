from django.db import models
from api.base_models import TimeStampMixin
from api.users.models import User
import uuid

class Specialization(models.Model):
    """
    Specialization model to store the specialization of doctors.
    This model is used to categorize doctors based on their expertise.
    """

    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    

class Doctor(TimeStampMixin):
    """
    Doctor model to store doctor information.
    This model includes the Django User model and includes additional fields
    specific to the doctor.
    """

    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="doctor"
    )
    specialization = models.ForeignKey(
        Specialization, on_delete=models.DO_NOTHING, related_name="doctors"
    )


class TimeSlot(models.Model):
    """
    TimeSlot model to store the time slots available for doctors.
    This model is used to manage the availability of doctors.
    """

    doctor = models.ForeignKey(
        Doctor, on_delete=models.CASCADE, related_name="time_slots"
    )
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.doctor.user.get_full_name()} - {self.start_time} to {self.end_time}"