import sys
import stripe
import logging
from decimal import Decimal
from django.db import transaction
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated

from api.payments.models import AppointmentPayment
from api.payments.serializers import AppointmentPaymentSerializer
from api.payments.choices import PaymentStatusChoices
from api.appointments.models import Appointment
from api.appointments.choices import Status as AppointmentStatus

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class CreatePaymentIntentView(APIView):
    """
    Create a Stripe Payment Intent for appointment payment.
    """

    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        try:
            serializer = AppointmentPaymentSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # Extract data from serializer
            validated_data = serializer.validated_data
            appointment_uuid = validated_data.get("appointment_uuid")
            amount = validated_data.get("amount")
            currency = validated_data.get("currency", "usd")
            receipt_email = validated_data.get("receipt_email", None)

            # Before the query, add:
            print(appointment_uuid)
            if not hasattr(request.user, "patient"):
                return Response({"error": "User has no patient profile"}, status=400)
            appointment = Appointment.objects.get(
                uuid=appointment_uuid, patient=request.user.patient
            )

            # Convert amount to cents (Stripe requirement)
            amount_decimal = Decimal(str(amount))
            amount_cents = int(amount_decimal * 100)

            # Create Stripe Payment Intent
            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency,
                metadata={
                    "appointment_uuid": str(appointment_uuid),
                    "patient_id": str(appointment.patient.id),
                    "doctor_id": (
                        str(appointment.time_slot.doctor.id)
                        if appointment.time_slot
                        else None
                    ),
                },
                receipt_email=receipt_email,
                automatic_payment_methods={
                    "enabled": True,
                },
            )

            payment = serializer.save(
                appointment=appointment,
                stripe_payment_intent_id=payment_intent.id,
                stripe_client_secret=payment_intent.client_secret,
                amount=amount_decimal,
                currency=currency,
                receipt_email=receipt_email or "",
            )

            return Response(AppointmentPaymentSerializer(payment).data)

        except Appointment.DoesNotExist:
            return Response(
                {"error": "Appointment not found"}, status=status.HTTP_404_NOT_FOUND
            )

        except serializers.ValidationError as e:
            logger.error(f"Validation error in payment creation: {str(e)}")
            stripe.PaymentIntent.cancel(payment_intent.id)
            return Response(
                {"error": "Validation error", "details": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            return Response(
                {"error": "Payment processing error", "details": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            logger.error(f"Unexpected error in payment creation: {str(e)}")
            return Response(
                {"error": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        finally:
            if "payment_intent" in locals() and sys.exc_info()[0] is not None:
                try:
                    stripe.PaymentIntent.cancel(payment_intent.id)
                    logger.info(
                        f"Canceled payment intent {payment_intent.id} due to exception"
                    )
                except Exception as cancel_error:
                    logger.error(f"Error canceling payment intent: {cancel_error}")


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(APIView):
    """
    Handle Stripe webhooks for payment status updates.
    """
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

        try:
            # Verify webhook signature
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except ValueError:
            logger.error("Invalid payload in Stripe webhook")
            return Response({"error": "Value error in construct_event"}, status=400)
        except stripe.error.SignatureVerificationError:
            logger.error("Invalid signature in Stripe webhook")
            return Response({"error": "Invalid signature"}, status=400)

        # Handle the event
        if event["type"] == "payment_intent.succeeded":
            self._handle_payment_succeeded(event["data"]["object"])
        elif event["type"] == "payment_intent.payment_failed":
            self._handle_payment_failed(event["data"]["object"])
        elif event["type"] == "payment_intent.canceled":
            self._handle_payment_canceled(event["data"]["object"])
        elif event["type"] == "payment_intent.requires_action":
            self._handle_payment_requires_action(event["data"]["object"])
        else:
            logger.info(f"Unhandled event type: {event['type']}")

        return Response({"error": "Invalid signature"}, status=200)

    def _handle_payment_succeeded(self, payment_intent):
        """Handle successful payment."""
        try:
            payment = AppointmentPayment.objects.get(
                stripe_payment_intent_id=payment_intent["id"]
            )

            # Update payment status
            payment.status = PaymentStatusChoices.SUCCEEDED
            payment.save(update_fields=["status"])

            # Update appointment status to PAID
            if payment.appointment:
                payment.appointment.status = AppointmentStatus.CONFIRMED
                payment.appointment.save(update_fields=["status"])

            logger.info(f"Payment succeeded: {payment_intent['id']}")

        except AppointmentPayment.DoesNotExist:
            logger.error(
                f"Payment not found for payment_intent: {payment_intent['id']}"
            )

    def _handle_payment_failed(self, payment_intent):
        """Handle failed payment."""
        try:
            payment = AppointmentPayment.objects.get(
                stripe_payment_intent_id=payment_intent["id"]
            )

            # Update payment status
            payment.status = PaymentStatusChoices.CANCELED
            payment.save(update_fields=["status"])

            # Optionally update appointment status
            if payment.appointment:
                payment.appointment.status = AppointmentStatus.CANCELLED
                payment.appointment.save(update_fields=["status"])

            logger.info(f"Payment failed: {payment_intent['id']}")

        except AppointmentPayment.DoesNotExist:
            logger.error(
                f"Payment not found for payment_intent: {payment_intent['id']}"
            )

    def _handle_payment_canceled(self, payment_intent):
        """Handle canceled payment."""
        try:
            payment = AppointmentPayment.objects.get(
                stripe_payment_intent_id=payment_intent["id"]
            )

            # Update payment status
            payment.status = PaymentStatusChoices.CANCELED
            payment.save(update_fields=["status"])

            # Update appointment status
            if payment.appointment:
                payment.appointment.status = AppointmentStatus.CANCELED
                payment.appointment.save(update_fields=["status"])

            logger.info(f"Payment canceled: {payment_intent['id']}")

        except AppointmentPayment.DoesNotExist:
            logger.error(
                f"Payment not found for payment_intent: {payment_intent['id']}"
            )

    def _handle_payment_requires_action(self, payment_intent):
        """Handle payment that requires additional action."""
        try:
            payment = AppointmentPayment.objects.get(
                stripe_payment_intent_id=payment_intent["id"]
            )

            # Update payment status
            payment.status = PaymentStatusChoices.REQUIRES_ACTION
            payment.save(update_fields=["status"])

            logger.info(f"Payment requires action: {payment_intent['id']}")

        except AppointmentPayment.DoesNotExist:
            logger.error(
                f"Payment not found for payment_intent: {payment_intent['id']}"
            )
