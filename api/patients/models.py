from django.db import models
from api.base_models import TimeStampMixin
import config.settings.base as settings


class Patient(TimeStampMixin):
    VISIT_TYPES = [
        ("SCREENING", "Screening"),
        ("DIAGNOSIS", "Diagnosis"),
        ("SURVEILLANCE", "Surveillance"),
        ("SECOND_OPINION", "Second Opinion"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="patient"
    )
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=20)
    visit_type = models.CharField(max_length=20, choices=VISIT_TYPES)  
    # will add extra details when needed for appointments api

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.gender}"

