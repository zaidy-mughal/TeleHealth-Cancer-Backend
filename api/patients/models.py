from django.db import models
from api.base_models import TimeStampMixin
import config.settings.base as settings
import uuid


class Patient(TimeStampMixin):
    """
    Patient model to store patient information.
    This model includes the Django User model and includes additional fields
    specific to the patient.
    """

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

    uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False, primary_key=True)

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="patient"
    )

    visit_type = models.CharField(max_length=20, choices=VisitType.choices)
    marital_status = models.CharField(max_length=20, choices=MaritalStatus.choices)
    sex_assign_at_birth = models.CharField(max_length=20)
    state = models.CharField(max_length=20)
    city = models.CharField(max_length=20)
    zip_code = models.CharField(max_length=20)
    is_iodine_contrast_allergic = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.get_full_name()}"


class Allergy(models.Model):
    """
    Allergy model to store patient's allergy information.
    """

    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="allergies"
    )
    allergy_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.allergy_name}"


class Medication(models.Model):
    """
    Medication model to store patient's medication history.
    """

    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="medications"
    )
    medication_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.medication_name}"


class MedicalHistory(models.Model):
    """
    Medical History model to store patient's medical history.
    """

    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="medical_history"
    )
    medical_condition = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.medical_condition}"


class SurgicalHistory(models.Model):
    """
    Surgical History model to store patient's surgical history.
    """

    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="surgical_history"
    )
    surgical_condition = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.surgical_condition}"


class CancerType(models.Model):
    """
    Cancer Type model to use it in Cancer History.
    """

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class CancerHistory(models.Model):
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
        CancerType, on_delete=models.CASCADE, related_name="cancer_history"
    )
    year_of_diagnosis = models.IntegerField()
    treatment_received = models.CharField(
        max_length=100, choices=TreatmentReceived.choices
    )

    def __str__(self):
        return f"{self.cancer_type.name}"


class Addiction(models.Model):
    """
    Addiction model to store patient's addiction history.
    """

    class AddictionType(models.TextChoices):
        SMOKING = "SMOKING", "Smoking"
        ALCOHOL = "ALCOHOL", "Alcohol"

    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="addiction_history"
    )
    addiction_type = models.CharField(max_length=100, choices=AddictionType.choices)
    year_of_addiction = models.IntegerField()
    description = models.TextField()

    def __str__(self):
        return f"{self.addiction_type}"


class PrimaryPhysician(models.Model):
    """
    Primary Physician model to store patient's primary physician information.
    """

    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="primary_physician"
    )
    name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.name}"


class Pharmacist(models.Model):
    """
    Pharmacist model to store patient's pharmacist information.
    """

    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="pharmacist"
    )
    name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.name}"
