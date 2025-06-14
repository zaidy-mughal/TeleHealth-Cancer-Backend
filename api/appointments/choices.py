from django.db import models


class Status(models.IntegerChoices):
    PENDING = 0, "Pending"
    CONFIRMED = 1, "Confirmed"
    CANCELLED = 2, "Cancelled"
    RESCHEDULED = 3, "Rescheduled"
    FAILED = 4, "Failed"
