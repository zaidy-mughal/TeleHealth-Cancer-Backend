from django.db import models

class Services(models.IntegerChoices):
    SERVEILLANCE = 0, "Serveillance"
    DIAGNOSIS = 1, "Diagnosis"
    SCREENING = 2, "Screening"
    SECOND_OPINION = 3, "Second Opinion"
