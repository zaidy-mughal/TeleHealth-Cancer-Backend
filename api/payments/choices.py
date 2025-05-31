from django.db import models


class PaymentStatusChoices(models.IntegerChoices):
    REQUIRES_PAYMENT_METHOD = 1, "Requires Payment Method"
    REQUIRES_CONFIRMATION = 2, "Requires Confirmation"
    REQUIRES_ACTION = 3, "Requires Action"
    PROCESSING = 4, "Processing"
    SUCCEEDED = 5, "Succeeded"
    CANCELED = 6, "Canceled"
    FAILED = 7, "Failed"
