from rest_framework import serializers
from api.appointments.models import Appointment
from api.appointments.choices import Status
from api.payments.models import AppointmentPayment
from api.payments.choices import PaymentStatusChoices


def validate_currency(value):
    """Validate currency code."""
    supported_currencies = ["usd", "eur", "gbp", "cad", "aud"]
    if value.lower() not in supported_currencies:
        raise serializers.ValidationError(
            f"Currency '{value}' is not supported. Supported currencies: {', '.join(supported_currencies)}"
        )
    return value.lower()


def validate_appointment(appointment_uuid):
    """Validate appointment exists and is valid for payment."""

    try:
        appointment = Appointment.objects.get(uuid=appointment_uuid)

        if (
            appointment.status == 1 or appointment.status == 2
        ):  # 1 is confirmed and 2 is completed
            raise serializers.ValidationError(
                "Cannot create payment for an appointment that is not confirmed."
            )
        return appointment
    except Appointment.DoesNotExist:
        raise serializers.ValidationError("Appointment does not exist.")


def validate_pending_payments(timeslot):
    """Check if there are pending payments for the timeslot."""

    pending_payments = AppointmentPayment.objects.filter(
        time_slot=timeslot,
        status__in=[
            PaymentStatusChoices.REQUIRES_PAYMENT_METHOD,
            PaymentStatusChoices.REQUIRES_CONFIRMATION,
            PaymentStatusChoices.PROCESSING,
        ],
    )

    if pending_payments.exists():
        raise serializers.ValidationError(
            "There's already a pending payment for this timeslot."
        )
    return timeslot


def validate_appointment_payment(appointment_uuid):
    """Validate that the payment exists and is valid for the appointment."""

    try:
        payment = AppointmentPayment.objects.get(appointment__uuid=appointment_uuid)

        if payment.status != PaymentStatusChoices.SUCCEEDED:
            raise serializers.ValidationError("Only succeeded payments can be refunded")

        if not payment.appointment:
            raise serializers.ValidationError("Payment has no associated appointment")

        if payment.refunds.filter(status=PaymentStatusChoices.SUCCEEDED).exists():
            raise serializers.ValidationError("Payment already has a succeeded refund")

    except AppointmentPayment.DoesNotExist:
        raise serializers.ValidationError("Payment not found")
