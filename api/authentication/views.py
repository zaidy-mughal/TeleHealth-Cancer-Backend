from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import LoginView, PasswordResetView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from api.authentication.serializers import (
    TeleHealthLoginSerializer,
    TeleHealthRegisterSerializer,
    OTPPasswordResetSerializer,
    OTPVerificationSerializer,
)

@method_decorator(csrf_exempt, name='dispatch')
class TeleHealthRegisterView(RegisterView):
    """
    Custom registration view for TeleHealth
    """
    serializer_class = TeleHealthRegisterSerializer

@method_decorator(csrf_exempt, name='dispatch')
class TeleHealthLoginView(LoginView):
    """
    Custom login view for TeleHealth
    """
    serializer_class = TeleHealthLoginSerializer

@method_decorator(csrf_exempt, name='dispatch')
class TeleHealthPasswordResetView(PasswordResetView):
    """
    Custom password reset view that sends OTP instead of reset link
    """
    serializer_class = OTPPasswordResetSerializer

@method_decorator(csrf_exempt, name='dispatch')
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
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
