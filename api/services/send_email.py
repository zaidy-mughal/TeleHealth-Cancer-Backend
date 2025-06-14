from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class EmailService:
    """Modular email service for sending templated emails"""

    @staticmethod
    def send_templated_email(
        template_name,
        subject,
        recipient_list,
        context=None,
        from_email=None,
        fail_silently=False,
        attachments=None,
    ):
        """
        Send templated email with HTML and plain text versions

        Args:
            template_name: Name of the template (without .html extension)
            subject: Email subject
            recipient_list: List of recipient email addresses
            context: Template context variables
            from_email: Sender email (defaults to DEFAULT_FROM_EMAIL)
            fail_silently: Whether to suppress exceptions
            attachments: List of file attachments

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        try:
            context = context or {}
            from_email = from_email or settings.DEFAULT_FROM_EMAIL

            html_template = f"emails/{template_name}.html"
            html_content = render_to_string(html_template, context)

            text_content = strip_tags(html_content)

            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email,
                to=recipient_list,
            )

            email.attach_alternative(html_content, "text/html")

            if attachments:
                for attachment in attachments:
                    email.attach(*attachment)

            email.send(fail_silently=fail_silently)

            logger.info(
                f"Successfully sent templated email to {', '.join(recipient_list)}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to send templated email: {str(e)}")
            if not fail_silently:
                raise
            return False

    @staticmethod
    def send_otp_email(user, otp: str) -> bool:
        context = {
            "user": user,
            "otp": otp,
            "expiry_minutes": settings.OTP_EXPIRY_MINUTES,
        }

        return EmailService.send_templated_email(
            template_name="otp_reset",
            subject="One-Time Passcode - TeleHealth",
            recipient_list=[user.email],
            context=context,
        )

    @staticmethod
    def send_welcome_email(user) -> bool:
        context = {"user": user}

        return EmailService.send_templated_email(
            template_name="welcome",
            subject="Welcome to TeleHealth",
            recipient_list=[user.email],
            context=context,
        )

    @staticmethod
    def send_appointment_confirmation_email(
        user, appointment_details: Dict[str, Any], payment_id, amount_paid
    ) -> bool:
        context = {
            "user": user,
            "appointment": appointment_details,
            "doctor_name": appointment_details.get("doctor_name", "Doctor"),
            "appointment_date": appointment_details.get("date", "Date"),
            "appointment_time": appointment_details.get("time", "Time"),
            "payment_id": payment_id,
            "amount_paid": amount_paid,
        }

        return EmailService.send_templated_email(
            template_name="appointment_confirmation",
            subject="Appointment Confirmation - TeleHealth",
            recipient_list=[user.email],
            context=context,
        )

    @staticmethod
    def send_payment_failed_email(
        user, appointment_details: Dict[str, Any], payment_id, amount
    ) -> bool:
        context = {
            "user": user,
            "appointment": appointment_details,
            "doctor_name": appointment_details.get("doctor_name", "Doctor"),
            "appointment_date": appointment_details.get("date", "Date"),
            "appointment_time": appointment_details.get("time", "Time"),
            "payment_id": payment_id,
            "amount": amount,
        }

        return EmailService.send_templated_email(
            template_name="payment_failed",
            subject="Payment Failed - TeleHealth",
            recipient_list=[user.email],
            context=context,
        )

    @staticmethod
    def send_refund_success_email(
        user, appointment_details, refund_amount, original_amount
    ):
        context = {
            "user": user,
            "appointment": appointment_details,
            "doctor_name": appointment_details.get("doctor_name", "Doctor"),
            "appointment_date": appointment_details.get("date", "Date"),
            "appointment_time": appointment_details.get("time", "Time"),
            "refund_amount": refund_amount,
            "original_amount": original_amount,
        }

        return EmailService.send_templated_email(
            template_name="refund_success",
            subject="Refund Successful - TeleHealth",
            recipient_list=[user.email],
            context=context,
        )

    @staticmethod
    def send_refund_failed_email(
        user, appointment_details, refund_amount, failure_reason
    ):
        context = {
            "user": user,
            "appointment": appointment_details,
            "doctor_name": appointment_details.get("doctor_name", "Doctor"),
            "appointment_date": appointment_details.get("date", "Date"),
            "appointment_time": appointment_details.get("time", "Time"),
            "refund_amount": refund_amount,
            "failure_reason": failure_reason,
        }

        return EmailService.send_templated_email(
            template_name="refund_failed",
            subject="Refund Failed - TeleHealth",
            recipient_list=[user.email],
            context=context,
        )
