from django.urls import path, include
from api.authentication.views import (
    TeleHealthRegisterView,
    TeleHealthLoginView,
    TeleHealthPasswordResetView,
    OTPVerificationView,
    PasswordChangeView,
)
from dj_rest_auth.views import LogoutView
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView


urlpatterns = [
    path("register/", TeleHealthRegisterView.as_view(), name="register"),
    path("login/", TeleHealthLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
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
