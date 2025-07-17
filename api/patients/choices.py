from django.db import models


class MaritalStatus(models.IntegerChoices):
    MARRIED = 0, "Married"
    SINGLE = 1, "Single"
    DIVORCED = 2, "Divorced"
    WIDOWED = 3, "Widowed"
    SEPARATED = 4, "Separated"
    OTHER = 5, "Other"


class Gender(models.IntegerChoices):
    MALE = 0, "Male"
    FEMALE = 1, "Female"
    OTHER = 2, "Other"


class TreatmentType(models.TextChoices):
    CHEMOTHERAPY = "chemotherapy", "Chemotherapy"
    RADIATION = "radiation", "Radiation Therapy"
    SURGERY = "surgery", "Surgery"
    OTHER = "other", "Other"


class AddictionType(models.TextChoices):
    SMOKING = "smoking", "Smoking"
    ALCOHOL = "alcohol", "Alcohol"


class IsIodineAllergic(models.TextChoices):
    NO = "no", "No"
    YES = "yes", "Yes"
    UNKNOWN = "unknown", "Unknown"

class CareProviderType(models.TextChoices):
    PRIMARY_PHYSICIAN = "primary_physician", "Primary Physician"
    PHARMACIST = "pharmacist", "Pharmacist"
