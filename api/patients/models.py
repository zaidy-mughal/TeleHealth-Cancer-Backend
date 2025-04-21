from django.db import models
from api.base_models import TimeStampMixin
import config.settings.base as settings
import uuid
from api.patients.choices import Gender, VisitType, MaritalStatus

from phonenumber_field.modelfields import PhoneNumberField


class Patient(TimeStampMixin):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="patient"
    )
    date_of_birth = models.DateField()
    gender = models.CharField(
        max_length=10, choices=Gender.choices, null=True, blank=True
    )
    phone_number = PhoneNumberField()
    visit_type = models.CharField(
        max_length=20, choices=VisitType.choices, null=True, blank=True
    )
    marital_status = models.CharField(
        max_length=20, choices=MaritalStatus.choices, null=True, blank=True
    )
    sex_assign_at_birth = models.CharField(max_length=20, null=True, blank=True)
    state = models.CharField(max_length=20, null=True, blank=True)
    city = models.CharField(max_length=20, null=True, blank=True)
    zip_code = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.gender}"


class IodineAllergy(models.Model):
    patient = models.OneToOneField(
        Patient, on_delete=models.CASCADE, related_name="iodine_allergy"
    )
    is_allergic = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.patient.user.get_full_name()} - {'Allergic' if self.is_allergic else 'Not Allergic'}"
