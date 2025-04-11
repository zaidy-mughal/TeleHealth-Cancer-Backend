from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import LoginView
from drf_spectacular.utils import extend_schema
from .serializers import (
    CustomRegisterSerializer,
    CustomLoginSerializer,
)

@extend_schema(
    request=CustomRegisterSerializer,
    tags=["Auth"],
    summary="Register a new user",
)
class CustomRegisterView(RegisterView):
    serializer_class = CustomRegisterSerializer


@extend_schema(
    request=CustomLoginSerializer,
    tags=["Auth"],
    summary="Log in user and return JWT tokens",
)
class CustomLoginView(LoginView):
    serializer_class = CustomLoginSerializer
