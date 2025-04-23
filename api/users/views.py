from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from api.users.serializers import UserSerializer
from api.users.models import User
from drf_spectacular.utils import extend_schema


@extend_schema(
    request=UserSerializer, responses={200: {"example": {"exists": True, "password_match": True}}}
)
class CheckUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data
        email = validated_data["email"]
        password1 = validated_data["password1"]
        password2 = validated_data["password2"]

        exists = User.objects.filter(email=email).exists()
        password_match = password1 == password2

        return Response(
            {"exists": exists, "password_match": password_match},
            status=status.HTTP_200_OK,
        )
