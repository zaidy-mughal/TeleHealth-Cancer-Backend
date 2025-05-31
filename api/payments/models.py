from django.db import models
from api.base_models import BaseModel
from api.appointments.models import Appointment
from api.payments.choices import PaymentStatusChoices


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

    # appointment association
    appointment = models.ForeignKey(
        "appointments.Appointment",
        on_delete=models.SET_NULL,
        null=True,
        related_name="payments",
    )

    payment_method_id = models.CharField(max_length=255, blank=True)
    receipt_email = models.EmailField(blank=True)

    def __str__(self):
        return f"Payment for Appointment {self.appointment} - {self.status}"
