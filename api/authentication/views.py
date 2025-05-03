from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import LoginView, PasswordResetView, LogoutView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers

from dj_rest_auth.views import PasswordResetView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.mail import send_mail
from django.conf import settings
import logging
from drf_spectacular.utils import extend_schema

from api.authentication.serializers import (
    TeleHealthLoginSerializer,
    TeleHealthRegisterSerializer,
    OTPPasswordResetSerializer,
    OTPVerificationSerializer,
    PasswordChangeSerializer,
    TeleHealthLogoutSerializer,
)

logger = logging.getLogger(__name__)


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
        headers = self.get_success_headers(serializer.data)
    
        user_data = self.get_response_data(user)

        # combined response with user data and profile_uuid as separate fields
        response_data = {
            'user': user_data,
        }
        if hasattr(serializer, 'profile_uuid') and serializer.profile_uuid:
            response_data['profile_uuid'] = str(serializer.profile_uuid)

        return Response(
            response_data,
            status=status.HTTP_201_CREATED,
            headers=headers,
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
        if hasattr(self, 'user'):
            data = self.serializer.validated_data
            profile_uuid = data.get('profile_uuid')
            
            if isinstance(response.data, dict):
                response.data['profile_uuid'] = profile_uuid
        
        return response


@method_decorator(csrf_exempt, name="dispatch")
class TeleHealthPasswordResetView(PasswordResetView):
    """
    Custom password reset view that sends OTP instead of reset link
    """

    serializer_class = OTPPasswordResetSerializer

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


class PasswordChangeView(APIView):
    """
    Custom password change view
    """

    permission_classes = [AllowAny]
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



class TeleHealthLogoutView(LogoutView):
    serializer_class = TeleHealthLogoutSerializer

    def post(self, request):
        try:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            response = super().logout(request)

            return response
        
        except serializers.ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
