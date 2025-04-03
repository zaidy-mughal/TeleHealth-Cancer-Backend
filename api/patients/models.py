from django.db import models
from api.users.models import User  # Custom user model
from api.base_models import TimeStampMixin


class Patient(TimeStampMixin):
    VISIT_TYPES = [
        ("SCREENING", "Screening"),
        ("DIAGNOSIS", "Diagnosis"),
        ("SURVEILLANCE", "Surveillance"),
        ("SECOND_OPINION", "Second Opinion"),
    ]

    CANCER_TYPES = [
        ("BLOOD_CANCER", "Blood Cancer"),
        ("LUNG_CANCER", "Lung Cancer"),
        ("BREAST_CANCER", "Breast Cancer"),
        ("COLON_CANCER", "Colon Cancer"),
        ("PROSTATE_CANCER", "Prostate Cancer"),
        ("OTHER", "Other"),
    ]

    CANCER_DURATION_CHOICES = [
        ("LESS_THAN_1_YEAR", "Less than 1 Year"),
        ("1_YEAR", "1 Year"),
        ("2_YEARS", "2 Years"),
        ("3_YEARS", "3 Years"),
        ("MORE_THAN_3_YEARS", "More than 3 Years"),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="patient_profile"
    )
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=20)

    physician_name = models.CharField(max_length=255, blank=True, null=True)
    physician_contact_number = models.CharField(max_length=20, blank=True, null=True)

    pharmacist_name = models.CharField(max_length=255, blank=True, null=True)
    pharmacist_contact_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        ordering = ["-created_at"]
