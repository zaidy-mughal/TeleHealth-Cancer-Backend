from enum import unique
from django.db import models
from django.contrib.auth import get_user_model

from api.base_models import BaseModel
from api.doctors.choices import Services, StateChoices

User = get_user_model()


class Specialization(BaseModel):
    """
    Specialization model to store the specialization of doctors.
    This model is used to categorize doctors based on their expertise.
    """

    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Specialization"
        verbose_name_plural = "Specializations"
        db_table = "specialization"


class Doctor(BaseModel):
    """
    Doctor model to store doctor information.
    This model includes the Django User model and includes additional fields
    specific to the doctor.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="doctor")
    specialization = models.ForeignKey(
        Specialization, on_delete=models.RESTRICT, related_name="doctors"
    )
    date_of_birth = models.DateField()
    address = models.CharField(max_length=255)
    npi_number = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return self.user.get_full_name()

    class Meta:
        verbose_name = "Doctor"
        verbose_name_plural = "Doctors"
        db_table = "doctor"
        indexes = [
            models.Index(fields=["specialization"]),
        ]


class Service(BaseModel):
    """
    Services model to store the services provided by doctors.
    """

    name = models.IntegerField(choices=Services.choices)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"
        db_table = "services"


class DoctorService(BaseModel):
    """
    DoctorServices Junction model to store the many-to-many relationship.
    """

    doctor = models.ForeignKey(
        Doctor, on_delete=models.CASCADE, related_name="doctor_services"
    )
    service = models.ForeignKey(
        Service, on_delete=models.RESTRICT, related_name="doctor_services"
    )

    def __str__(self):
        return f"{self.doctor.user.get_full_name()} - {self.service.name}"

    class Meta:
        verbose_name = "Doctor Service"
        verbose_name_plural = "Doctor Services"
        db_table = "doctor_services"
        unique_together = ("doctor", "service")


class TimeSlot(BaseModel):
    """
    TimeSlot model to store the time slots available for doctors.
    This model is used to manage the availability of doctors.
    """

    doctor = models.ForeignKey(
        Doctor, on_delete=models.CASCADE, related_name="time_slots"
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_booked = models.BooleanField(db_default=False)

    def __str__(self):
        return (
            f"{self.doctor.user.get_full_name()} - {self.start_time} to {self.end_time}"
        )

    class Meta:
        verbose_name = "Time Slot"
        verbose_name_plural = "Time Slots"
        db_table = "time_slot"
        indexes = [
            models.Index(fields=["doctor"]),
        ]


class LicenseInfo(BaseModel):
    """
    LicenseInfo model to store the license information of doctors.
    This model is used to manage the licensing information of doctors.
    """

    doctor = models.ForeignKey(
        Doctor, on_delete=models.CASCADE, related_name="license_info"
    )
    license_number = models.CharField(max_length=20, unique=True)
    state = models.IntegerField(choices=StateChoices.choices)  # try django cities

    def __str__(self):
        return f"{self.doctor.user.get_full_name()} - {self.license_number}"

    class Meta:
        verbose_name = "License Info"
        verbose_name_plural = "License Info"
        db_table = "license_info"
        indexes = [
            models.Index(fields=["doctor"]),
        ]
