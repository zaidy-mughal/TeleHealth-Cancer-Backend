from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
import logging
from typing import Dict, List, Any

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

            # Render HTML template
            html_template = f"emails/{template_name}.html"
            html_content = render_to_string(html_template, context)

            # Create plain text version by stripping HTML tags
            text_content = strip_tags(html_content)

            # Create email message
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=from_email,
                to=recipient_list,
            )

            # Attach HTML version
            email.attach_alternative(html_content, "text/html")

            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    email.attach(*attachment)

            # Send email
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
        """Send OTP email using template"""
        context = {
            "user": user,
            "otp": otp,
            "expiry_minutes": settings.OTP_EXPIRY_MINUTES,
        }

        return EmailService.send_templated_email(
            template_name="otp_reset",
            subject="Password Reset OTP - TeleHealth",
            recipient_list=[user.email],
            context=context,
        )

    @staticmethod
    def send_welcome_email(user) -> bool:
        """Send welcome email to new user"""
        context = {
            "user": user,
            "login_url": (
                f"{settings.FRONTEND_URL}/login"
                if hasattr(settings, "FRONTEND_URL")
                else "#"
            ),
        }

        return EmailService.send_templated_email(
            template_name="welcome",
            subject="Welcome to TeleHealth",
            recipient_list=[user.email],
            context=context,
        )

    @staticmethod
    def send_appointment_confirmation_email(user, appointment_details: Dict[str, Any]) -> bool:
        """Send appointment confirmation email"""
        context = {
            "user": user,
            "appointment": appointment_details,
            "doctor_name": appointment_details.get("doctor_name", "Doctor"),
            "appointment_date": appointment_details.get("date", "Date"),
            "appointment_time": appointment_details.get("time", "Time"),
        }

        return EmailService.send_templated_email(
            template_name="appointment_confirmation",
            subject="Appointment Confirmation - TeleHealth",
            recipient_list=[user.email],
            context=context,
        )
    
    
    @staticmethod
    def send_payment_failed_email(user, appointment_details: Dict[str, Any]) -> bool:
        """Send payment failed email"""
        context = {
            "user": user,
            "appointment": appointment_details,
            "doctor_name": appointment_details.get("doctor_name", "Doctor"),
            "appointment_date": appointment_details.get("date", "Date"),
            "appointment_time": appointment_details.get("time", "Time"),
        }

        return EmailService.send_templated_email(
            template_name="payment_failed",
            subject="Payment Failed - TeleHealth",
            recipient_list=[user.email],
            context=context,
        )
