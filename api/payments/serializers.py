from rest_framework import serializers
from decimal import Decimal
from django.core.validators import EmailValidator
from api.payments.models import AppointmentPayment
from api.appointments.serializers import AppointmentSerializer
from api.payments.validators import validate_currency, validate_appointment


class AppointmentPaymentSerializer(serializers.ModelSerializer):
    """
    Serializer for AppointmentPayment model with validation and security.
    """

    stripe_payment_intent_id = serializers.CharField(read_only=True)
    stripe_client_secret = serializers.CharField(read_only=True)

    appointment_details = AppointmentSerializer(source="appointment", read_only=True)
    payment_status = serializers.CharField(source="get_status_display", read_only=True)

    appointment_uuid = serializers.UUIDField(write_only=True, required=True)
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
            "stripe_payment_intent_id",
            "stripe_client_secret",
            "amount",
            "currency",
            "payment_status",
            "appointment_uuid",
            "appointment_details",
            "payment_method_id",
            "receipt_email",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "stripe_payment_intent_id",
            "stripe_client_secret",
            "created_at",
            "updated_at",
            "appointment_details",
            "payment_status",
        ]

    def create(self, validated_data):
        appointment_uuid = validated_data.pop("appointment_uuid")
        return super().create(validated_data)

    def validate(self, attrs):
        currency = attrs.get("currency", "usd")
        validate_currency(currency)

        appointment_uuid = attrs.get("appointment_uuid")
        validate_appointment(appointment_uuid)

        return attrs
