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
    gender = models.CharField(max_length=10, choices=Gender.choices, blank=True)
    phone_number = PhoneNumberField()
    visit_type = models.CharField(max_length=20, choices=VisitType.choices, blank=True)
    marital_status = models.CharField(max_length=20, choices=MaritalStatus.choices, blank=True)
    sex_assign_at_birth = models.CharField(max_length=20, blank=True)
    state = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=20, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)

    allergies = models.ManyToManyField("Allergy", related_name="patients", blank=True)
    medications = models.ManyToManyField("Medication", related_name="patients", blank=True)
    medical_history = models.ManyToManyField("MedicalHistory", related_name="patients", blank=True)
    surgical_history = models.ManyToManyField("SurgicalHistory", related_name="patients", blank=True)

    pharmacist = models.ForeignKey(
        "Pharmacist", on_delete=models.SET_NULL, related_name="patients", null=True, blank=True
    )
    primary_physician = models.ForeignKey(
        "PrimaryPhysician", on_delete=models.SET_NULL, related_name="patients", null=True, blank=True
    )
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


class Allergy(TimeStampMixin):
    """
    Allergy model to store patient's allergy information.
    """
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"


class Medication(TimeStampMixin):
    """
    Medication model to store patient's medication history.
    """
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"


class MedicalHistory(TimeStampMixin):
    """
    Medical History model to store patient's medical history.
    """
    medical_condition = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.medical_condition}"


class SurgicalHistory(TimeStampMixin):
    """
    Surgical History model to store patient's surgical history.
    """
    surgical_condition = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.surgical_condition}"


class CancerType(TimeStampMixin):
    """
    Cancer Type model to use it in Cancer History.
    """
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class CancerHistory(TimeStampMixin):
    """
    Cancer History model to store patient's cancer history.
    """
    class TreatmentReceived(models.TextChoices):
        CHEMOTHERAPY = "CHEMOTHERAPY", "Chemotherapy"
        RADIATION = "RADIATION", "Radiation Therapy"
        SURGERY = "SURGERY", "Surgery"
        OTHER = "OTHER", "Other"

    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="cancer_history"
    )
    cancer_type = models.ForeignKey(
        CancerType, on_delete=models.CASCADE, related_name="cancer_type"
    )
    year_of_diagnosis = models.IntegerField()
    treatment_received = models.CharField(max_length=100, choices=TreatmentReceived.choices)

    def __str__(self):
        return f"{self.cancer_type.name}"


class AddictionHistory(TimeStampMixin):
    """
    Smoking and Alcohol History model to store patient's smoking history.
    """
    class AddictionType(models.TextChoices):
        SMOKING = "SMOKING", "Smoking"
        ALCOHOL = "ALCOHOL", "Alcohol"

    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="addiction_history"
    )

    addiction_type = models.CharField(max_length=20, choices=AddictionType.choices, null=True, blank=True)
    description = models.TextField()
    total_years = models.IntegerField()

    def __str__(self):
        return f"{self.addiction_type}"


class PrimaryPhysician(TimeStampMixin):
    """
    Primary Physician model to store patient's primary physician information.
    """
    name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.name}"


class Pharmacist(TimeStampMixin):
    """
    Pharmacist model to store patient's pharmacist information.
    """
    name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.name}"


