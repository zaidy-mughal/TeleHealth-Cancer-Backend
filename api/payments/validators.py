from rest_framework import serializers
from api.appointments.models import Appointment


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
            appointment.status != 1 and appointment.status != 2
        ):  # 1 is confirmed and 2 is completed
            raise serializers.ValidationError(
                "Cannot create payment for an appointment that is not confirmed."
            )
        return appointment
    except Appointment.DoesNotExist:
        raise serializers.ValidationError("Appointment does not exist.")
