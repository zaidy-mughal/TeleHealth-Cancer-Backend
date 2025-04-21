from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import LoginView
from drf_spectacular.utils import extend_schema

from api.authentication.serializers import (
    TeleHealthRegisterSerializer,
    TeleHealthLoginSerializer
)

@extend_schema(
    request=TeleHealthRegisterSerializer,
    tags=["Auth"],
    summary="Register a new user",
)
class TeleHealthRegisterView(RegisterView):
    serializer_class = TeleHealthRegisterSerializer


@extend_schema(
    request=TeleHealthLoginSerializer,
    tags=["Auth"],
    summary="Log in user and return JWT tokens",
)
class TeleHealthLoginView(LoginView):
    serializer_class = TeleHealthLoginSerializer
