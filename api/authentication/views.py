from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import LoginView, PasswordResetView, LogoutView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import logging

from api.authentication.choices import Purpose
from api.utils.exception_handler import HandleExceptionAPIView
from api.authentication.serializers import (
    TeleHealthLoginSerializer,
    TeleHealthRegisterSerializer,
    RequestOTPSerializer,
    OTPVerificationSerializer,
    PasswordChangeSerializer,
)

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class TeleHealthRegisterView(HandleExceptionAPIView, RegisterView):
    """
    Custom registration view for TeleHealth
    """

    serializer_class = TeleHealthRegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)

        user_data = self.get_response_data(user)

        # combined response
        if hasattr(serializer, "profile_uuid") and serializer.profile_uuid:
            user_data["profile_uuid"] = str(serializer.profile_uuid)

        return Response(
            user_data,
            status=status.HTTP_201_CREATED,
        )


@method_decorator(csrf_exempt, name="dispatch")
class TeleHealthLoginView(HandleExceptionAPIView, LoginView):
    """
    Custom login view for TeleHealth
    """

    serializer_class = TeleHealthLoginSerializer
    permission_classes = [AllowAny]

    def get_response(self):
        response = super().get_response()

        if hasattr(self, "user"):
            data = self.serializer.validated_data
            profile_uuid = data.get("profile_uuid")

            if isinstance(response.data, dict):
                response.data["profile_uuid"] = profile_uuid

        response.data.pop("access", None)
        response.data.pop("refresh", None)

        return response


@method_decorator(csrf_exempt, name="dispatch")
class TeleHealthPasswordResetView(HandleExceptionAPIView, PasswordResetView):
    """
    Custom password reset view that sends OTP instead of reset link
    """

    permission_classes = [AllowAny]
    serializer_class = RequestOTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"detail": "Password reset OTP has been sent to your email."},
            status=status.HTTP_200_OK,
        )


@method_decorator(csrf_exempt, name="dispatch")
class PasswordChangeView(HandleExceptionAPIView, APIView):
    """
    Custom password change view
    """

    permission_classes = [AllowAny]
    serializer_class = PasswordChangeSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Password changed successfully"},
            status=status.HTTP_200_OK,
        )


@method_decorator(csrf_exempt, name="dispatch")
class TeleHealthLogoutView(HandleExceptionAPIView, LogoutView):
    """
    Custom logout view that clears JWT cookies
    """
    serializer_class = None
    permission_classes = [IsAuthenticated]
    http_method_names = ["post"]

    def logout(self, request):
        response = super().logout(request)

        response.delete_cookie("telehealth-access-token")
        response.delete_cookie("telehealth-refresh-token")

        response.data = {"detail": "Successfully logged out."}
        return response


class SendOTPView(HandleExceptionAPIView, APIView):
    permission_classes = [AllowAny]
    serializer_class = RequestOTPSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        return Response(result, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name="dispatch")
class VerifyEmailOTPView(HandleExceptionAPIView, APIView):
    """
    Verify email with OTP during registration
    """

    permission_classes = [AllowAny]
    serializer_class = OTPVerificationSerializer

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={"purpose": Purpose.EMAIL_VERIFICATION}
        )

        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        logger.info(
            f"Email verification successful for email: "
            f"{request.data.get('email', 'unknown')}"
        )
        return Response(result, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name="dispatch")
class VerifyPasswordResetOTPView(HandleExceptionAPIView, APIView):
    """
    Verify OTP for password reset
    """

    permission_classes = [AllowAny]
    serializer_class = OTPVerificationSerializer

    def post(self, request):
        serializer = self.serializer_class(
            data=request.data, context={"purpose": Purpose.PASSWORD_RESET}
        )

        serializer.is_valid(raise_exception=True)
        result = serializer.save()
        logger.info(
            f"Password reset OTP verification successful for email: "
            f"{request.data.get('email', 'unknown')}"
        )
        return Response(result, status=status.HTTP_200_OK)
