from django.db import models


class Role(models.IntegerChoices):
    ADMIN = 0, "Admin"
    DOCTOR = 1, "Doctor"
    PATIENT = 2, "Patient"
    NURSE = 3, "Nurse"
