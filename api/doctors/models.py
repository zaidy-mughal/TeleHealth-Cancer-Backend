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
    class Services(models.TextChoices):
        SERVEILLANCE = "SERVEILLANCE", "Serveillance"
        DIAGNOSIS = "DIAGNOSIS", "Diagnosis"
        SCREENING = "SCREENING", "Screening"
        SECOND_OPINION = "SECOND_OPINION", "Second Opinion"

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="doctor"
    )
    specialization = models.ForeignKey(
        Specialization, on_delete=models.DO_NOTHING, related_name="doctors"
    )
    date_of_birth = models.DateField()
    address = models.CharField(max_length=255)
    npi_number = models.CharField(max_length=20, unique=True)
    services = models.CharField(max_length=255, choices=Services.choices, null=True, blank=True)


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


class LicenseInfo(models.Model):
    """
    LicenseInfo model to store the license information of doctors.
    This model is used to manage the licensing information of doctors.
    """
    doctor = models.ForeignKey(
        Doctor, on_delete=models.CASCADE, related_name="license_info"
    )
    license_number = models.CharField(max_length=20, unique=True)
    state = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.doctor.user.get_full_name()} - {self.license_number}"