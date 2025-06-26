from django.db import models
from django.contrib.auth import get_user_model
from phonenumber_field.modelfields import PhoneNumberField

from api.base_models import BaseModel
from api.patients.choices import (
    Gender,
    MaritalStatus,
)

User = get_user_model()


class Patient(BaseModel):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="patient")
    date_of_birth = models.DateField()
    gender = models.IntegerField(choices=Gender.choices, blank=True, null=True)
    phone_number = PhoneNumberField()
    marital_status = models.IntegerField(
        choices=MaritalStatus.choices, blank=True, null=True
    )
    sex_assigned_at_birth = models.CharField(max_length=20, blank=True)
    state = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=20, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)

    class Meta:
        verbose_name = "Patient"
        verbose_name_plural = "Patients"
        db_table = "patient"
        indexes = [
            models.Index(fields=["state"]),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.gender}"


class PatientMedicalRecord(BaseModel):
    """
    Patient Medical Record model to store patient's medical records.
    """

    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="medical_records"
    )

    is_main_record = models.BooleanField(default=False)

    appointment_uuid = models.UUIDField(
        null=True,
        blank=True,
        help_text="UUID of the appointment to update the seperate fields consistently.",
    )

    iodine_allergy = models.JSONField(
        default=dict,
        help_text="Iodine allergy information: {'is_iodine_allergic':bool}",
    )
    allergies = models.JSONField(
        default=dict, help_text="All allergies: [{'name':str}, ...]"
    )
    medications = models.JSONField(
        default=dict, help_text="All medications: [{'name':str}, ...]"
    )
    medical_histories = models.JSONField(
        default=dict, help_text="All medical histories: [{'name':str}, ...]"
    )
    surgical_histories = models.JSONField(
        default=dict, help_text="All surgical histories: [{'name':str}, ...]"
    )
    cancer_history = models.JSONField(
        default=dict,
        help_text="Patient's Cancer History: [{'cancer_type':choice, 'year_of_diagnosis':year, 'treatment_received':[{'name':choice},...],},]",
    )
    addiction_history = models.JSONField(
        default=dict,
        help_text="Patient's Addiction History: [{'addiction_type':choice, 'total_years':str}, ...] | Exactly two addiction types are required (one for smoking and one for alcohol).",
    )
    care_providers = models.JSONField(
        default=dict,
        help_text="Patient Care Providers: [{'name':str, 'contact_number':phone, 'type': choice}] | Maximum 2 care providers are allowed | one for type 1 and second for type 2",
    )

    def __str__(self):
        return f"{self.patient.user.get_full_name()}"

    class Meta:
        verbose_name = "Patient Medical Record"
        verbose_name_plural = "Patient Medical Records"
        db_table = "patient_medical_record"
