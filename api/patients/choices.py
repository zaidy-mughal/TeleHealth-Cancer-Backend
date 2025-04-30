from django.db import models


class VisitType(models.IntegerChoices):
    CANCER_SCREENING = 0, "Cancer Screening"
    SECOND_OPINION = 1, "Cancer Treatment Second Opinion"
    SURVEILLANCE = 2, "Cancer Surveillance"
    NURSE_SUPPORT = 3, "Oncology Nurse Support"
    FOLLOW_UP = 4, "Follow-Up Visit"
    INITIAL_CONSULT = 5, "Initial Consultation"


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
    NON_BINARY = 2, "Non-binary"
    PREFER_NOT_TO_SAY = 3, "Prefer not to say"


class TreatmentReceived(models.IntegerChoices):
    CHEMOTHERAPY = 0, "Chemotherapy"
    RADIATION = 1, "Radiation Therapy"
    SURGERY = 2, "Surgery"
    OTHER = 3, "Other"


class AddictionType(models.IntegerChoices):
    SMOKING = 0, "Smoking"
    ALCOHOL = 1, "Alcohol"