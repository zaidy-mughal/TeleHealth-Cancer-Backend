from django.db import models


class Status(models.IntegerChoices):
    PENDING = 0, "Pending"
    CONFIRMED = 1, "Confirmed"
    CANCELLED = 2, "Cancelled"
    CANCELED_REFUNDED = 6, "Canceled_Refunded"
