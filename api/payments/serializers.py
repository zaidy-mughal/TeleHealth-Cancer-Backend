from rest_framework import serializers
from decimal import Decimal
from django.core.validators import EmailValidator

from api.payments.models import AppointmentPayment
from api.payments.validators import validate_currency, validate_pending_payments
from api.doctors.models import TimeSlot
from api.doctors.validators import (
    validate_booked_slot,
    validate_start_time_lt_end_time,
    future_start_time,
)


class AppointmentPaymentSerializer(serializers.ModelSerializer):
    """
    Serializer for AppointmentPayment without nested details.
    """

    stripe_payment_intent_id = serializers.CharField(read_only=True)
    stripe_client_secret = serializers.CharField(read_only=True)
    payment_status = serializers.CharField(source="get_status_display", read_only=True)

    time_slot_uuid = serializers.UUIDField(required=True)

    currency = serializers.CharField(max_length=3, default="usd")
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal("0.50"),
        max_value=Decimal("999999.99"),
    )

    receipt_email = serializers.EmailField(
        required=False, allow_blank=True, validators=[EmailValidator()]
    )
    payment_method_id = serializers.CharField(
        max_length=255, required=False, allow_blank=True
    )

    class Meta:
        model = AppointmentPayment
        fields = [
            "id",
            "uuid",
            "stripe_payment_intent_id",
            "stripe_client_secret",
            "amount",
            "currency",
            "payment_status",
            "time_slot_uuid",
            "payment_method_id",
            "receipt_email",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "uuid",
            "stripe_payment_intent_id",
            "stripe_client_secret",
            "payment_status",
            "created_at",
            "updated_at",
        ]

    def validate_time_slot_uuid(self, value):
        try:
            time_slot = TimeSlot.objects.get(uuid=value)

            validate_booked_slot(time_slot)
            validate_start_time_lt_end_time(time_slot.start_time, time_slot.end_time)
            future_start_time(time_slot.start_time)
            validate_pending_payments(time_slot)

            return value

        except TimeSlot.DoesNotExist:
            raise serializers.ValidationError("Timeslot not found.")

    def validate_currency(self, value):
        """Validate currency code."""
        return validate_currency(value)

    def create(self, validated_data):
        """Create AppointmentPayment with timeslot and patient"""
        time_slot_uuid = validated_data.pop("time_slot_uuid")
        time_slot = TimeSlot.objects.get(uuid=time_slot_uuid)

        request = self.context.get("request")
        if not request or not hasattr(request.user, "patient"):
            raise serializers.ValidationError("User must have a patient profile.")

        patient = request.user.patient

        appointment_payment = AppointmentPayment.objects.create(
            time_slot=time_slot, patient=patient, **validated_data
        )

        return appointment_payment
