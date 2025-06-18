from django.db import models


class PaymentStatusChoices(models.IntegerChoices):
    REQUIRES_PAYMENT_METHOD = 1, "Requires Payment Method"
    REQUIRES_CONFIRMATION = 2, "Requires Confirmation"
    REQUIRES_ACTION = 3, "Requires Action"
    PROCESSING = 4, "Processing"
    SUCCEEDED = 5, "Succeeded"
    CANCELED = 6, "Canceled"
    REFUNDED = 7, "Refunded"
    FAILED = 8, "Failed"


class RefundPolicyChoices(models.IntegerChoices):
    FULL_REFUND = 1, "Full Refund"
    PARTIAL_REFUND = 2, "Partial Refund"
    NO_REFUND = 3, "No Refund"


class RefundPaymentChoices(models.IntegerChoices):
    REQUIRES_ACTION = 1, "Requires Action"
    SUCCEEDED = 2, "Succeeded"
    FAILED = 3, "Failed"
    CANCELLED = 4, "Cancelled"
