import logging


from rest_framework import serializers
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
from django.core.validators import EmailValidator
from api.appointments.models import Appointment
from api.payments.models import (
    AppointmentPayment,
    RefundPolicy,
    AppointmentPaymentRefund,
)


logger = logging.getLogger(__name__)

from api.patients.utils.fields import LabelChoiceField
from api.payments.validators import (
    validate_currency,
    validate_pending_payments,
    validate_appointment_payment,
)
from api.payments.choices import (
    RefundPolicyChoices,
)
from api.doctors.models import TimeSlot
from api.doctors.validators import (
    validate_booked_slot,
    validate_start_time_lt_end_time,
    future_start_time,
)


class AppointmentPaymentSerializer(serializers.ModelSerializer):
    """
    Serializer for AppointmentPayment without nested details.
    Added a create and update method for the appointment_uuid field.
    """

    stripe_payment_intent_id = serializers.CharField(read_only=True)
    stripe_client_secret = serializers.CharField(read_only=True)
    payment_status = serializers.CharField(source="get_status_display", read_only=True)

    appointment_uuid = serializers.UUIDField(required=True, write_only=True)

    currency = serializers.CharField(max_length=3, default="usd")
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal("0.50"),
        max_value=Decimal("999999.99"),
    )

    receipt_email = serializers.EmailField(
        required=False, allow_blank=True
    )
    payment_method_id = serializers.CharField(
        max_length=255, required=False, allow_blank=True
    )

    class Meta:
        model = AppointmentPayment
        fields = [
            "uuid",
            "appointment_uuid",
            "stripe_payment_intent_id",
            "stripe_client_secret",
            "amount",
            "currency",
            "payment_status",
            "payment_method_id",
            "receipt_email",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "uuid",
            "stripe_payment_intent_id",
            "stripe_client_secret",
            "payment_status",
            "created_at",
            "updated_at",
        ]

    def validate_appointment_uuid(self, value):
        try:
            appointment = Appointment.objects.get(uuid=value)
            time_slot = appointment.time_slot

            validate_start_time_lt_end_time(time_slot.start_time, time_slot.end_time)
            future_start_time(time_slot.start_time)
            validate_pending_payments(appointment)

            return value

        except TimeSlot.DoesNotExist:
            raise serializers.ValidationError("Timeslot not found.")

    def validate_currency(self, value):
        return validate_currency(value)

    def create(self, validated_data):
        appointment_uuid = validated_data.pop("appointment_uuid")
        appointment = Appointment.objects.get(uuid=appointment_uuid)

        appointment_payment = AppointmentPayment.objects.create(
            appointment=appointment, **validated_data
        )
        return appointment_payment


class AppointmentRefundSerializer(serializers.ModelSerializer):
    """
    Serializer for AppointmentPaymentRefund with refund policy logic.
    """

    appointment_uuid = serializers.UUIDField(write_only=True)

    class Meta:
        model = AppointmentPaymentRefund
        fields = [
            "uuid",
            "appointment_uuid",
            "amount",
            "status",
            "reason",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "uuid",
            "amount",
            "status",
            "created_at",
            "updated_at",
        ]

    def _get_applicable_refund_policy(self, appointment_time):
        now = timezone.now()
        time_until_appointment = appointment_time - now
        hours_until = time_until_appointment.total_seconds() / 3600

        if hours_until < 4:
            # 0% refund
            return RefundPolicy.objects.filter(
                is_active=True, hours_before_min=0, hours_before_max=4
            ).first()
        elif hours_until < 24:
            # 50% refund
            return RefundPolicy.objects.filter(
                is_active=True, hours_before_min=4, hours_before_max=24
            ).first()
        else:
            # 100% refund
            return RefundPolicy.objects.filter(
                is_active=True, hours_before_min=24, hours_before_max=99999
            ).first()

    def validate(self, attrs):
        """Validate refund eligibility and find applicable policy"""
        appointment_uuid = attrs["appointment_uuid"]
        validate_appointment_payment(appointment_uuid)
        payment = AppointmentPayment.objects.get(appointment__uuid=appointment_uuid)

        if not payment.appointment or not payment.appointment.time_slot:
            raise serializers.ValidationError("Invalid appointment or time slot")

        appointment_time = payment.appointment.time_slot.start_time

        applicable_policy = self._get_applicable_refund_policy(appointment_time)

        if not applicable_policy:
            raise serializers.ValidationError("No active refund policy found")

        refund_amount = payment.amount * (applicable_policy.refund_percentage / 100)

        if refund_amount < 0:
            raise serializers.ValidationError("No refund available based on policy")

        attrs["_payment"] = payment
        attrs["_applicable_policy"] = applicable_policy
        attrs["_refund_amount"] = refund_amount

        return attrs

    def create(self, validated_data):
        payment = validated_data.pop("_payment")
        applicable_policy = validated_data.pop("_applicable_policy")
        refund_amount = validated_data.pop("_refund_amount")

        refund = AppointmentPaymentRefund.objects.create(
            appointment_payment=payment,
            refund_policy=applicable_policy,
            amount=refund_amount,
            reason=validated_data.get(
                "reason", f"Refund based on {applicable_policy.name}"
            ),
        )

        return refund


class RefundPolicySerializer(serializers.ModelSerializer):
    """
    Serializer for RefundPolicy.
    """

    refund_type = LabelChoiceField(choices=RefundPolicyChoices.choices, required=True)

    class Meta:
        model = RefundPolicy
        fields = [
            "id",
            "uuid",
            "name",
            "refund_type",
            "hours_before_min",
            "hours_before_max",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "uuid", "created_at", "updated_at"]
