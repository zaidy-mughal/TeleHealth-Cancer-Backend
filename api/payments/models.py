from django.db import models
from api.base_models import BaseModel
from api.payments.choices import (
    PaymentStatusChoices,
    RefundPolicyChoices,
    RefundPaymentChoices,
)
from django.core.exceptions import ObjectDoesNotExist
from api.appointments.models import Appointment

class AppointmentPayment(BaseModel):
    """
    Model to store appointment payment details.
    """

    stripe_payment_intent_id = models.CharField(max_length=255, unique=True)
    stripe_client_secret = models.CharField(max_length=255)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default="usd")
    status = models.IntegerField(
        choices=PaymentStatusChoices.choices,
        default=PaymentStatusChoices.REQUIRES_PAYMENT_METHOD,
    )

    time_slot = models.ForeignKey(
        "doctors.TimeSlot",
        on_delete=models.CASCADE,
        related_name="payment_reservations",
        null=True,
        blank=True,
    )

    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="payments",
        null=True,
        blank=True,
    )

    appointment = models.ForeignKey(
        "appointments.Appointment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
    )

    appointment_uuid = models.UUIDField(
        null=True,
        blank=True,
        help_text="UUID of the related appointment",
        db_index=True,
    )    
    
    payment_method_id = models.CharField(max_length=255, blank=True)
    receipt_email = models.EmailField(blank=True)

    def __str__(self):
        return f"Payment for Appointment {self.appointment} - {self.status}"



class RefundPolicy(BaseModel):
    """
    Refund policy for appointments
    """

    name = models.CharField(max_length=100)
    refund_type = models.IntegerField(
        choices=RefundPolicyChoices.choices
    )
    hours_before_min = models.PositiveIntegerField(
        help_text="Minimum hours before the appointment to apply this refund policy"
    )
    hours_before_max = models.PositiveIntegerField(
        help_text="Maximum hours before the appointment to apply this refund policy"
    )
    refund_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=100.00
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} - {self.get_refund_type_display()}"


class AppointmentPaymentRefund(BaseModel):
    """
    Model to store appointment payment refund details.
    """

    appointment_payment = models.ForeignKey(
        AppointmentPayment,
        on_delete=models.CASCADE,
        related_name="refunds",
        help_text="The payment that is being refunded",
    )

    refund_policy = models.ForeignKey(
        RefundPolicy,
        on_delete=models.SET_NULL,
        related_name="refunds",
        help_text="Refund policy applied to this refund",
        null=True,
        blank=True,
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.IntegerField(
        choices=RefundPaymentChoices.choices,
        default=RefundPaymentChoices.REQUIRES_ACTION,
    )

    reason = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Refund for Payment {self.appointment_payment} - {self.status}"
