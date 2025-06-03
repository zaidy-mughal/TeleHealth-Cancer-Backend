from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import LoginView, PasswordResetView, LogoutView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import logging

from api.authentication.choices import Purpose
from api.authentication.serializers import (
    TeleHealthLoginSerializer,
    TeleHealthRegisterSerializer,
    RequestOTPSerializer,
    OTPVerificationSerializer,
    PasswordChangeSerializer,
    TeleHealthLogoutSerializer,
)


logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class TeleHealthRegisterView(RegisterView):
    """
    Custom registration view for TeleHealth
    """

    serializer_class = TeleHealthRegisterSerializer

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)

        user_data = self.get_response_data(user)

        # combined response with user data and profile_uuid as separate fields
        if hasattr(serializer, "profile_uuid") and serializer.profile_uuid:
            user_data["profile_uuid"] = str(serializer.profile_uuid)

        return Response(
            user_data,
            status=status.HTTP_201_CREATED,
        )


@method_decorator(csrf_exempt, name="dispatch")
class TeleHealthLoginView(LoginView):
    """
    Custom login view for TeleHealth
    """

    serializer_class = TeleHealthLoginSerializer

    def get_response(self):
        response = super().get_response()

        # Add profile_uuid to the response data
        if hasattr(self, "user"):
            data = self.serializer.validated_data
            profile_uuid = data.get("profile_uuid")

            if isinstance(response.data, dict):
                response.data["profile_uuid"] = profile_uuid

        return response


@method_decorator(csrf_exempt, name="dispatch")
class TeleHealthPasswordResetView(PasswordResetView):
    """
    Custom password reset view that sends OTP instead of reset link
    """

    serializer_class = RequestOTPSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(
                {"detail": "Password reset OTP has been sent to your email."},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"Password reset error: {str(e)}")
            return Response(
                {"detail": f"Error during password reset: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@method_decorator(csrf_exempt, name="dispatch")
class OTPVerificationView(APIView):
    """
    Custom OTP verification view
    """

    permission_classes = [AllowAny]
    serializer_class = OTPVerificationSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                return Response({"detail": "OTP verified successfully"})
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"OTP verification error: {str(e)}")
            return Response(
                {"detail": f"Error during OTP verification: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@method_decorator(csrf_exempt, name="dispatch")
class PasswordChangeView(APIView):
    """
    Custom password change view
    """

    permission_classes = [IsAuthenticated]
    serializer_class = PasswordChangeSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    {"detail": "Password changed successfully"},
                    status=status.HTTP_200_OK,
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Password change error: {str(e)}")
            return Response(
                {"detail": f"Error during password change: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@method_decorator(csrf_exempt, name="dispatch")
class TeleHealthLogoutView(LogoutView):
    serializer_class = TeleHealthLogoutSerializer

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)

            response = super().logout(request)
            return response

        except serializers.ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SendOTPView(APIView):
    permission_classes = [AllowAny]
    serializer_class = RequestOTPSerializer

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)

            if serializer.is_valid():
                result = serializer.save()
                return Response(result, status=status.HTTP_200_OK)

        except serializers.ValidationError as e:
            logger.error(f"Validation error in SendOTPView: {str(e)}")
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Unexpected error in SendOTPView: {str(e)}")
            return Response(
                {"detail": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@method_decorator(csrf_exempt, name="dispatch")
class VerifyEmailOTPView(APIView):
    """
    Verify email with OTP during registration
    """

    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = OTPVerificationSerializer(
                data=request.data, context={"purpose": Purpose.EMAIL_VERIFICATION}
            )

            if serializer.is_valid():
                result = serializer.save()
                logger.info(
                    f"Email verification successful for email: {request.data.get('email', 'unknown')}"
                )
                return Response(result, status=status.HTTP_200_OK)

            logger.warning(
                f"Email verification failed - validation errors: {serializer.errors}"
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except serializers.ValidationError as e:
            logger.error(f"Validation error in VerifyEmailOTPView: {str(e)}")
            return Response(
                {"detail": "Invalid data provided for email verification"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            logger.error(f"Unexpected error in VerifyEmailOTPView: {str(e)}")
            return Response(
                {
                    "detail": f"An unexpected error occurred during email verification: {str(e)}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@method_decorator(csrf_exempt, name="dispatch")
class VerifyPasswordResetOTPView(APIView):
    """
    Verify OTP for password reset
    """

    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = OTPVerificationSerializer(
                data=request.data, context={"purpose": Purpose.PASSWORD_RESET}
            )

            if serializer.is_valid():
                result = serializer.save()
                logger.info(
                    f"Password reset OTP verification successful for email: {request.data.get('email', 'unknown')}"
                )
                return Response(result, status=status.HTTP_200_OK)

            logger.warning(
                f"Password reset OTP verification failed - validation errors: {serializer.errors}"
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except serializers.ValidationError as e:
            logger.error(f"Validation error in VerifyPasswordResetOTPView: {str(e)}")
            return Response(
                {"detail": "Invalid data provided for password reset OTP verification"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as e:
            logger.error(f"Unexpected error in VerifyPasswordResetOTPView: {str(e)}")
            return Response(
                {
                    "detail": f"An unexpected error occurred during password reset OTP verification: {str(e)}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@method_decorator(csrf_exempt, name="dispatch")
def account_inactive_view(request):
    return Response(
        {"detail": "Your account is inactive. Please verify your email."}, status=403
    )
