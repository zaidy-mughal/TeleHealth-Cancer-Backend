from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from api.users.serializers import CheckSerializer
from api.users.models import User

import logging

logger = logging.getLogger(__name__)


@extend_schema(
    request=CheckSerializer,
    responses={200: {"example": {"exists": True, "password_match": True}}},
)
@method_decorator(csrf_exempt, name="dispatch")
class CheckUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = CheckSerializer(data=request.data)
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

        except Exception as e:
            logger.error(f"Error in CheckUserView: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
