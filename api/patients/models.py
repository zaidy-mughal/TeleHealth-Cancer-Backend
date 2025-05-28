from django.db import models
from django.contrib.auth import get_user_model
from phonenumber_field.modelfields import PhoneNumberField
from cities_light.models import City, Region


from api.base_models import BaseModel
from api.patients.choices import (
    Gender,
    VisitType,
    MaritalStatus,
    TreatmentType,
    AddictionType,
    IsIodineAllergic,
    CareProviderType,
)

User = get_user_model()


class Patient(BaseModel):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="patient")
    date_of_birth = models.DateField()
    gender = models.IntegerField(choices=Gender.choices, blank=True, null=True)
    phone_number = PhoneNumberField()
    visit_type = models.IntegerField(choices=VisitType.choices, blank=True, null=True)
    marital_status = models.IntegerField(
        choices=MaritalStatus.choices, blank=True, null=True
    )
    sex_assigned_at_birth = models.CharField(max_length=20, blank=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True)
    state = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)

    class Meta:
        verbose_name = "Patient"
        verbose_name_plural = "Patients"
        db_table = "patient"
        indexes = [
            models.Index(fields=["visit_type"]),
            models.Index(fields=["state"]),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.gender}"


class IodineAllergy(BaseModel):
    patient = models.OneToOneField(
        Patient, on_delete=models.CASCADE, related_name="iodine_allergy"
    )
    is_iodine_allergic = models.IntegerField(choices=IsIodineAllergic.choices)

    def __str__(self):
        return f"{self.patient.user.get_full_name()} - {'Allergic' if self.is_iodine_allergic else 'Not Allergic'}"

    class Meta:
        verbose_name = "Iodine Allergy"
        verbose_name_plural = "Iodine Allergies"
        db_table = "iodine_allergy"


class Allergy(BaseModel):
    """
    Allergy model to store patient's allergy information.
    """

    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Allergy"
        verbose_name_plural = "Allergies"
        db_table = "allergy"


class Medication(BaseModel):
    """
    Medication model to store patient's medication history.
    """

    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = "Medication"
        verbose_name_plural = "Medications"
        db_table = "medication"


class MedicalHistory(BaseModel):
    """
    Medical History model to store patient's medical history.
    """

    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.medical_condition}"

    class Meta:
        verbose_name = "Medical History"
        verbose_name_plural = "Medical Histories"
        db_table = "medical_history"


class SurgicalHistory(BaseModel):
    """
    Surgical History model to store patient's surgical history.
    """

    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.surgical_condition}"

    class Meta:
        verbose_name = "Surgical History"
        verbose_name_plural = "Surgical Histories"
        db_table = "surgical_history"


class CancerType(BaseModel):
    """
    Cancer Type model to use it in Cancer History.
    """

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Cancer Type"
        verbose_name_plural = "Cancer Types"
        db_table = "cancer_type"


class CancerHistory(BaseModel):
    """
    Cancer History model to store patient's cancer history.
    """

    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="cancer_history"
    )
    cancer_type = models.ForeignKey(
        CancerType, on_delete=models.RESTRICT, related_name="cancer_type"
    )
    year_of_diagnosis = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.cancer_type.name}"

    class Meta:
        verbose_name = "Cancer History"
        verbose_name_plural = "Cancer Histories"
        db_table = "cancer_history"


class TreatmentRecieved(BaseModel):
    """
    Treatment Recieved model to use it in Cancer History.
    """

    cancer_history = models.ForeignKey(
        CancerHistory, on_delete=models.CASCADE, related_name="treatment_received"
    )

    name = models.IntegerField(choices=TreatmentType.choices, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Treatment Recieved"
        verbose_name_plural = "Treatment Recieveds"
        db_table = "treatment_recieved"


class AddictionHistory(BaseModel):
    """
    Smoking and Alcohol History model to store patient's smoking history.
    """

    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="addiction_history"
    )

    addiction_type = models.IntegerField(choices=AddictionType.choices, blank=True)
    total_years = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.addiction_type}"

    class Meta:
        verbose_name = "Addiction History"
        verbose_name_plural = "Addiction Histories"
        db_table = "addiction_history"


class CareProvider(BaseModel):
    """
    Patient Care Provider model to store patient's care provider information.
    """

    name = models.CharField(max_length=100)
    contact_number = PhoneNumberField()
    type = models.IntegerField(CareProviderType.choices)

    class Meta:
        verbose_name = "Care Provider"
        verbose_name_plural = "Care Providers"
        db_table = "care_provider"


# ALL JUNCTION TABLES
class PatientAllergy(models.Model):
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="allergies"
    )
    allergy = models.ForeignKey(
        Allergy, on_delete=models.RESTRICT, related_name="allergy_patients"
    )

    class Meta:
        verbose_name = "Patient Allergy"
        verbose_name_plural = "Patient Allergies"
        db_table = "patient_allergy"


class PatientMedication(models.Model):
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="medications"
    )
    medication = models.ForeignKey(
        Medication, on_delete=models.RESTRICT, related_name="medication_patients"
    )

    class Meta:
        verbose_name = "Patient Medication"
        verbose_name_plural = "Patient Medications"
        db_table = "patient_medication"


class PatientMedicalHistory(models.Model):
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="medical_histories"
    )
    medical_history = models.ForeignKey(
        MedicalHistory,
        on_delete=models.RESTRICT,
        related_name="medical_history_patients",
    )

    class Meta:
        verbose_name = "Patient Medical History"
        verbose_name_plural = "Patient Medical Histories"
        db_table = "patient_medical_history"


class PatientSurgicalHistory(models.Model):
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="surgical_histories"
    )
    surgical_history = models.ForeignKey(
        SurgicalHistory,
        on_delete=models.RESTRICT,
        related_name="surgical_history_patients",
    )

    class Meta:
        verbose_name = "Patient Surgical History"
        verbose_name_plural = "Patient Surgical Histories"
        db_table = "patient_surgical_history"


class PatientCareProvider(models.Model):
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="care_providers"
    )
    care_provider = models.ForeignKey(
        CareProvider, on_delete=models.RESTRICT, related_name="care_provider_patients"
    )

    class Meta:
        verbose_name = "Patient Care Provider"
        verbose_name_plural = "Patient Care Providers"
        db_table = "patient_care_provider"
