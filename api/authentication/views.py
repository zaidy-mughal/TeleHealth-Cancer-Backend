from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import LoginView
from dj_rest_auth.views import PasswordResetView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from dj_rest_auth.views import PasswordResetView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

from api.authentication.serializers import (
    TeleHealthLoginSerializer,
    TeleHealthRegisterSerializer,
    TeleHealthLoginSerializer,
    OTPPasswordResetSerializer,
    OTPVerificationSerializer,
    PasswordChangeSerializer,
)




class TeleHealthRegisterView(RegisterView):
    """
    Custom registration view for TeleHealth
    """

    serializer_class = TeleHealthRegisterSerializer


class TeleHealthLoginView(LoginView):
    """
    Custom login view for TeleHealth
    """

    serializer_class = TeleHealthLoginSerializer


class TeleHealthPasswordResetView(PasswordResetView):
    """
    Custom password reset view that sends OTP instead of reset link
    """

    serializer_class = OTPPasswordResetSerializer


class OTPVerificationView(APIView):
    """
    Custom OTP verification view
    """

    permission_classes = [AllowAny]
    serializer_class = OTPVerificationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            return Response({"detail": "OTP verified successfully"})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeView(APIView):
    """
    Custom password change view
    """

    permission_classes = [AllowAny]
    serializer_class = PasswordChangeSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"detail": "Password changed successfully"}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
