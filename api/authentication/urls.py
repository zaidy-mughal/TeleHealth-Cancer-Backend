from django.urls import path, include
from api.authentication.views import CustomRegisterView, CustomLoginView
from dj_rest_auth.views import (
    PasswordResetView, PasswordResetConfirmView, LogoutView, PasswordChangeView
)
from rest_framework_simplejwt.views import (TokenRefreshView, TokenVerifyView)


urlpatterns = [
    path('register/', CustomRegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('password/reset/', PasswordResetView.as_view(), name='password_reset'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_done'),
    path('password/change/', PasswordChangeView.as_view(), name='password_change'),

    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
