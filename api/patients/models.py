from django.db import models
from django.conf import settings
import uuid
from api.patients.choices import Gender, VisitType, MaritalStatus

from phonenumber_field.modelfields import PhoneNumberField


class Patient(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.gender}"


class IodineAllergy(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    patient = models.OneToOneField(
        Patient, on_delete=models.CASCADE, related_name="iodine_allergy"
    )
    is_allergic = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.patient.user.get_full_name()} - {'Allergic' if self.is_allergic else 'Not Allergic'}"


class Allergy(models.Model):
    """
    Allergy model to store patient's allergy information.
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"


class Medication(models.Model):
    """
    Medication model to store patient's medication history.
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"


class MedicalHistory(models.Model):
    """
    Medical History model to store patient's medical history.
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    medical_condition = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.medical_condition}"


class SurgicalHistory(models.Model):
    """
    Surgical History model to store patient's surgical history.
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    surgical_condition = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.surgical_condition}"


class CancerType(models.Model):
    """
    Cancer Type model to use it in Cancer History.
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class CancerHistory(models.Model):
    """
    Cancer History model to store patient's cancer history.
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
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


class AddictionHistory(models.Model):
    """
    Smoking and Alcohol History model to store patient's smoking history.
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
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


class PrimaryPhysician(models.Model):
    """
    Primary Physician model to store patient's primary physician information.
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.name}"


class Pharmacist(models.Model):
    """
    Pharmacist model to store patient's pharmacist information.
    """
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.name}"


