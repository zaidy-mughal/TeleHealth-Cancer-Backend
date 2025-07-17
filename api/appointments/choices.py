from django.db import models


class Status(models.IntegerChoices):
    PENDING = 0, "Pending"
    CONFIRMED = 1, "Confirmed"
    CANCELLED = 2, "Cancelled"
    REFUNDED = 3, "Refunded"
    COMPLETED = 4, "Completed"
    RESCHEDULED = 5, "Rescheduled"
    REFUND_PENDING = 6, "Refund Pending"
