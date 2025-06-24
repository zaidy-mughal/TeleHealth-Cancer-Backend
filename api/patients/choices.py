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


class TreatmentType(models.IntegerChoices):
    CHEMOTHERAPY = 0, "Chemotherapy"
    RADIATION = 1, "Radiation Therapy"
    SURGERY = 2, "Surgery"
    OTHER = 3, "Other"


class AddictionType(models.IntegerChoices):
    SMOKING = 0, "Smoking"
    ALCOHOL = 1, "Alcohol"


class IsIodineAllergic(models.IntegerChoices):
    NO = 0, "No"
    YES = 1, "Yes"
    UNKNOWN = 2, "Unknown"


class CareProviderType(models.IntegerChoices):
    PRIMARY_PHYSICIAN = 0, "Primary Physician"
    PHARMACIST = 1, "Pharmacist"
