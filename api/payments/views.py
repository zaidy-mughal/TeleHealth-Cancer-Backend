import sys
import stripe
import logging
from decimal import Decimal
from django.db import transaction
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from api.services.send_email import EmailService

from api.payments.models import AppointmentPayment
from api.payments.serializers import (
    AppointmentPaymentSerializer,
    AppointmentRefundSerializer,
)
from api.payments.choices import PaymentStatusChoices, RefundPaymentChoices
from api.appointments.choices import Status as AppointmentStatus
from api.utils.exception_handler import HandleExceptionAPIView
from api.patients.permissions import IsPatient

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class CreatePaymentIntentView(HandleExceptionAPIView, APIView):
    """
    Create a Stripe Payment Intent for appointment payment.
    """

    permission_classes = [IsAuthenticated, IsPatient]
    serializer_class = AppointmentPaymentSerializer

    @transaction.atomic
    def post(self, request):
        try:
            serializer = AppointmentPaymentSerializer(
                data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)

            validated_data = serializer.validated_data
            appointment_uuid = validated_data.get("appointment_uuid")
            amount = validated_data.get("amount")
            currency = validated_data.get("currency", "usd")

            amount_decimal = Decimal(str(amount))
            amount_cents = int(amount_decimal * 100)

            payment_intent = stripe.PaymentIntent.create(
                amount=amount_cents,
                currency=currency,
                metadata={
                    "appointment_uuid": str(appointment_uuid),
                },
                automatic_payment_methods={
                    "enabled": True,
                },
            )

            serializer.save(
                stripe_payment_intent_id=payment_intent.id,
                stripe_client_secret=payment_intent.client_secret,
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except stripe.error.StripeError as e:
            logger.error(f"Stripe error: {str(e)}")
            return Response(
                {"error": "Payment processing error"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        finally:
            # checks whether an error occurs and cancel the intent.
            if "payment_intent" in locals() and sys.exc_info()[0] is not None:
                try:
                    stripe.PaymentIntent.cancel(payment_intent.id)
                    logger.info(
                        f"Canceled payment intent {payment_intent.id} due to exception"
                    )
                except Exception as cancel_error:
                    logger.error(f"Error canceling payment intent: {cancel_error}")


@method_decorator(csrf_exempt, name="dispatch")
class AppointmentRefundView(HandleExceptionAPIView, APIView):
    """
    Create refund for appointment payment with policy validation.
    """

    permission_classes = [IsAuthenticated, IsPatient]
    serializer_class = AppointmentRefundSerializer

    @transaction.atomic
    def post(self, request):
        try:
            serializer = AppointmentRefundSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            appointment_uuid = serializer.validated_data["appointment_uuid"]
            payment = AppointmentPayment.objects.get(appointment__uuid=appointment_uuid)

            refund_record = serializer.save()

            refund_amount_cents = int(refund_record.amount * 100)

            stripe_refund = stripe.Refund.create(
                payment_intent=payment.stripe_payment_intent_id,
                amount=refund_amount_cents,
                reason="requested_by_customer",
                metadata={
                    "refund_id": str(refund_record.uuid),
                    "appointment_id": str(payment.appointment.uuid),
                },
            )

            refund_record.status = RefundPaymentChoices.REQUIRES_ACTION
            refund_record.save(update_fields=["status"])

            return Response(
                {
                    "message": "Refund processed successfully. You will receive an email shortly.",
                    "refund_details": AppointmentRefundSerializer(refund_record).data,
                    "stripe_refund_id": stripe_refund.id,
                },
                status=status.HTTP_200_OK,
            )

        except stripe.error.StripeError as e:
            if "refund_record" in locals():
                refund_record.status = PaymentStatusChoices.CANCELED
                refund_record.save(update_fields=["status"])
            logger.error(f"Stripe refund error: {str(e)}")
            return Response(
                {"error": f"Refund failed!"},
                status=status.HTTP_400_BAD_REQUEST,
            )


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(HandleExceptionAPIView, APIView):
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
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except ValueError:
            logger.error("Invalid payload in Stripe webhook")
            return Response({"error": "Value error in construct_event"}, status=400)
        except stripe.error.SignatureVerificationError:
            logger.error("Invalid signature in Stripe webhook")
            return Response(
                {"error": "Invalid signature"}, status=status.HTTP_400_BAD_REQUEST
            )

        if event["type"] == "payment_intent.requires_action":
            self._handle_payment_requires_action(event["data"]["object"])
        elif event["type"] == "payment_intent.succeeded":
            self._handle_payment_succeeded(event["data"]["object"])
        elif event["type"] == "payment_intent.payment_failed":
            self._handle_payment_failed(event["data"]["object"])
        elif event["type"] == "payment_intent.canceled":
            self._handle_payment_canceled(event["data"]["object"])

        # Refund Events
        elif event["type"] == "refund.created":
            self._handle_refund_created(event["data"]["object"])
        elif event["type"] == "refund.updated":
            self._handle_refund_updated(event["data"]["object"])
        elif event["type"] == "charge.refunded":
            self._handle_charge_refunded(event["data"]["object"])
        elif event["type"] == "refund.failed":
            self._handle_refund_failed(event["data"]["object"])

        # TODO: Dispute Events (related to refunds/chargebacks)
        # elif event["type"] == "charge.dispute.created":
        #     self._handle_dispute_created(event["data"]["object"])
        # elif event["type"] == "charge.dispute.updated":
        #     self._handle_dispute_updated(event["data"]["object"])
        # elif event["type"] == "charge.dispute.closed":
        #     self._handle_dispute_closed(event["data"]["object"])

        else:
            logger.info(f"Unhandled event type: {event['type']}")

        return Response({"status": "success"}, status=status.HTTP_200_OK)

    def _handle_payment_requires_action(self, payment_intent):
        """Handle payment that requires additional action."""
        try:
            payment = AppointmentPayment.objects.get(
                stripe_payment_intent_id=payment_intent["id"]
            )

            payment.status = PaymentStatusChoices.REQUIRES_ACTION
            payment.save(update_fields=["status"])

            logger.info(f"Payment requires action: {payment_intent['id']}")

        except AppointmentPayment.DoesNotExist:
            logger.error(
                f"Payment not found for payment_intent: {payment_intent['id']}"
            )

    def _handle_payment_succeeded(self, payment_intent):
        """Handle successful payment."""
        try:
            payment = AppointmentPayment.objects.get(
                stripe_payment_intent_id=payment_intent["id"]
            )

            payment.payment_method_id = payment_intent.get("payment_method", None)
            payment.status = PaymentStatusChoices.SUCCEEDED
            payment.save(update_fields=["status", "payment_method_id"])

            if not payment.appointment:
                logger.error(f"Payment {payment.uuid} has no associated appointment.")
                return

            payment.appointment.status = AppointmentStatus.CONFIRMED
            payment.appointment.save(update_fields=["status"])

            EmailService.send_appointment_confirmation_email(
                user=payment.appointment.medical_record.patient.user,
                appointment_details={
                    "doctor_name": payment.appointment.time_slot.doctor.user.get_full_name(),
                    "date": payment.appointment.time_slot.start_time.date(),
                    "time": payment.appointment.time_slot.start_time,
                },
                payment_id=payment.payment_method_id,
                amount_paid=payment.amount,
            )

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

            payment.status = PaymentStatusChoices.FAILED
            payment.save(update_fields=["status"])

            if not payment.appointment:
                logger.error(f"Payment {payment.uuid} has no associated appointment.")
                return

            payment.appointment.status = AppointmentStatus.FAILED
            payment.appointment.save(update_fields=["status"])

            EmailService.send_payment_failed_email(
                user=payment.appointment.medical_record.patient.user,
                appointment_details={
                    "doctor_name": payment.appointment.time_slot.doctor.user.get_full_name(),
                    "date": payment.appointment.time_slot.start_time.date(),
                    "time": payment.appointment.time_slot.start_time,
                },
                payment_id=payment.id,
                amount=payment.amount,
            )

            logger.info("Payment failed: %s", payment_intent['id'])

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

            payment.status = PaymentStatusChoices.CANCELED
            payment.save(update_fields=["status"])

            if not payment.appointment:
                logger.error(f"Payment {payment.uuid} has no associated appointment.")
                return

            payment.appointment.status = AppointmentStatus.CANCELED
            payment.appointment.save(update_fields=["status"])

            logger.info(f"Payment canceled: {payment_intent['id']}")

        except AppointmentPayment.DoesNotExist:
            logger.error(
                f"Payment not found for payment_intent: {payment_intent['id']}"
            )

    # REFUND HANDLING METHODS
    def _handle_charge_refunded(self, charge_obj):
        """Handle when a charge is refunded - main refund event."""
        logger.info(f"Handling charge.refunded for charge: {charge_obj['id']}")

        try:
            payment_intent_id = charge_obj.get("payment_intent")
            if not payment_intent_id:
                logger.error("No payment_intent found in charge object")
                return

            payment = AppointmentPayment.objects.get(
                stripe_payment_intent_id=payment_intent_id
            )

            refunds = charge_obj.get("refunds", {}).get("data", [])
            if not refunds:
                logger.warning(f"No refunds found in charge object: {charge_obj['id']}")
                return

            refund_data = refunds[0]
            refund_status = refund_data["status"]

            status_mapping = {
                "pending": RefundPaymentChoices.REQUIRES_ACTION,
                "succeeded": RefundPaymentChoices.SUCCEEDED,
                "failed": RefundPaymentChoices.FAILED,
                "canceled": RefundPaymentChoices.CANCELED,
            }

            mapped_status = status_mapping.get(
                refund_status, RefundPaymentChoices.REQUIRES_ACTION
            )

            refund_record = payment.refunds.first()

            if refund_record:
                refund_record.status = mapped_status
                refund_record.save(update_fields=["status"])

                logger.info(
                    f"Updated refund record {refund_record.id} to status: {mapped_status}"
                )

                if mapped_status == RefundPaymentChoices.SUCCEEDED:
                    payment.status = PaymentStatusChoices.REFUNDED
                    payment.appointment.status = AppointmentStatus.REFUNDED
                    payment.appointment.time_slot.is_booked = False

                    payment.appointment.time_slot.save(update_fields=["is_booked"])
                    payment.appointment.save(update_fields=["status"])
                    payment.save(update_fields=["status"])

                    logger.info(
                        f"Payment {payment.id} marked as refunded due to charge refund"
                    )

                    EmailService.send_refund_success_email(
                        user=payment.appointment.medical_record.patient.user,
                        appointment_details={
                            "doctor_name": payment.appointment.time_slot.doctor.user.get_full_name(),
                            "date": payment.appointment.time_slot.start_time.date(),
                            "time": payment.appointment.time_slot.start_time,
                        },
                        refund_amount=refund_record.amount,
                        original_amount=payment.amount,
                    )
            else:
                logger.error(f"No refund record found for payment {payment.id}")

        except AppointmentPayment.DoesNotExist:
            logger.error(f"Payment not found for payment_intent: {payment_intent_id}")
        except Exception as e:
            logger.error(f"Error in _handle_charge_refunded: {str(e)}")

    def _handle_refund_created(self, refund_obj):
        """Handle refund creation."""
        logger.info(f"Handling refund.created for refund: {refund_obj['id']}")

    def _handle_refund_updated(self, refund_obj):
        """Handle refund status updates."""
        logger.info(f"Handling refund.updated for refund: {refund_obj['id']}")

    def _handle_refund_failed(self, refund_obj):
        """Handle failed refund."""
        logger.info(f"Handling refund.failed for refund: {refund_obj['id']}")

        try:
            charge_id = refund_obj.get("charge")
            if not charge_id:
                logger.error("No charge found in refund object")
                return

            charge = stripe.Charge.retrieve(charge_id)
            payment_intent_id = charge.payment_intent

            payment = AppointmentPayment.objects.get(
                stripe_payment_intent_id=payment_intent_id
            )

            if payment.refunds.exists():
                refund_record = payment.refunds.first()
                refund_record.status = RefundPaymentChoices.FAILED
                refund_record.save(update_fields=["status"])

                if payment.appointment:
                    EmailService.send_refund_failed_email(
                        user=payment.appointment.medical_record.patient.user,
                        appointment_details={
                            "doctor_name": payment.appointment.time_slot.doctor.user.get_full_name(),
                            "date": payment.appointment.time_slot.start_time.date(),
                            "time": payment.appointment.time_slot.start_time,
                        },
                        refund_amount=refund_record.amount,
                        failure_reason=refund_obj.get(
                            "failure_reason", "Unknown error in while refunding payment"
                        ),
                    )
            else:
                logger.error(f"No refund record found for payment {payment.id}")

        except AppointmentPayment.DoesNotExist:
            logger.error(f"Payment not found for refund {refund_obj['id']}")
        except stripe.error.StripeError as e:
            logger.error(
                f"Error retrieving charge for refund {refund_obj['id']}: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error in _handle_refund_failed: {str(e)}")


class AppointmentPaymentUUIDView(APIView):
    
    def get(self, request, appointment_uuid):
        try:
            payment = AppointmentPayment.objects.get(appointment_uuid=appointment_uuid)
            return Response({"appointment_payment_uuid": str(payment.uuid)})
        except AppointmentPayment.DoesNotExist:
            return Response(
                {"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND
            )
