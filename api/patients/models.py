from django.db import models
from api.base_models import TimeStampMixin
import config.settings.base as settings
import uuid

class Patient(TimeStampMixin):
    class VisitType(models.TextChoices):
        CANCER_SCREENING = "CANCER_SCREENING", "Cancer Screening"
        SECOND_OPINION = "SECOND_OPINION", "Cancer Treatment Second Opinion"
        SURVEILLANCE = "SURVEILLANCE", "Cancer Surveillance"
        NURSE_SUPPORT = "NURSE_SUPPORT", "Oncology Nurse Support"
        FOLLOW_UP = "FOLLOW_UP", "Follow-Up Visit"
        INITIAL_CONSULT = "INITIAL_CONSULT", "Initial Consultation"

    class MaritalStatus(models.TextChoices):
        MARRIED = "MARRIED", "Married"
        SINGLE = "SINGLE", "Single"
        DIVORCED = "DIVORCED", "Divorced"
        WIDOWED = "WIDOWED", "Widowed"
        SEPARATED = "SEPARATED", "Separated"
        OTHER = "OTHER", "Other"

    class Gender(models.TextChoices):
        MALE = "MALE", "Male"
        FEMALE = "FEMALE", "Female"
        NON_BINARY = 'NB', 'Non-binary'
        PREFER_NOT_TO_SAY = 'NA', 'Prefer not to say'

    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False, primary_key=True)

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="patient"
    )
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10,choices=Gender.choices, null=True, blank=True)
    phone_number = models.CharField(max_length=20)
    visit_type = models.CharField(max_length=20, choices=VisitType.choices, null=True, blank=True)
    marital_status = models.CharField(max_length=20, choices=MaritalStatus.choices, null=True, blank=True)
    sex_assign_at_birth = models.CharField(max_length=20, null=True, blank=True)
    state = models.CharField(max_length=20, null=True, blank=True)
    city = models.CharField(max_length=20, null=True, blank=True)
    zip_code = models.CharField(max_length=20, null=True, blank=True)
    is_iodine_contrast_allergic = models.BooleanField(default=False, null=True, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.gender}"

