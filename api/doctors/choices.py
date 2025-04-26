from django.db import models

class Services(models.TextChoices):
    SERVEILLANCE = "SERVEILLANCE", "Serveillance"
    DIAGNOSIS = "DIAGNOSIS", "Diagnosis"
    SCREENING = "SCREENING", "Screening"
    SECOND_OPINION = "SECOND_OPINION", "Second Opinion"
