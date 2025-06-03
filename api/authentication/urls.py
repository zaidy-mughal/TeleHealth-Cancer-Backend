from django.urls import path
from api.authentication.views import (
    TeleHealthRegisterView,
    TeleHealthLoginView,
    TeleHealthPasswordResetView,
    OTPVerificationView,
    PasswordChangeView,
    TeleHealthLogoutView,
    SendOTPView,
)

from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView


urlpatterns = [
    path("register/", TeleHealthRegisterView.as_view(), name="register"),
    path("login/", TeleHealthLoginView.as_view(), name="login"),
    path("logout/", TeleHealthLogoutView.as_view(), name="logout"),
    path("otp/send/", SendOTPView.as_view(), name="send_otp"),
    path("email/otp/verify/", OTPVerificationView.as_view(), name="otp_verify"),
    path(
        "password/reset/", TeleHealthPasswordResetView.as_view(), name="password_reset"
    ),
    path(
        "password/reset/otp/verify/",
        OTPVerificationView.as_view(),
        name="password_reset_done",
    ),
    path("password/change/", PasswordChangeView.as_view(), name="password_change"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]
