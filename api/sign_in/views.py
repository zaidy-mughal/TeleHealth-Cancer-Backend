from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from .models import UserAccount
from .serializers import (
    RoleBasedRegistrationSerializer,
    UserRegistrationStep2Serializer,
    UserAccountSerializer,
    UserAccountUpdateSerializer,
)


class UserAccountViewSet(viewsets.ModelViewSet):

    queryset = UserAccount.objects.all()
    serializer_class = UserAccountSerializer
    permission_classes = [AllowAny]

    def get_serializer_class(self):

        if self.action == "register_step1":
            return RoleBasedRegistrationSerializer
        elif self.action == "register_step2":
            return UserRegistrationStep2Serializer
        elif self.action in ["update", "partial_update"]:
            return UserAccountUpdateSerializer
        return UserAccountSerializer

    @action(detail=False, methods=["post"], url_path="register-step1")
    def register_step1(self, request):

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {"message": "Step 1 completed successfully", "user_id": user.id},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="register-step2")
    def register_step2(self, request):

        user_id = request.data.get("user_id")
        if not user_id:
            return Response(
                {"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = get_object_or_404(UserAccount, pk=user_id)
        except Exception as e:
            return Response(
                {"error": f"User not found: {str(e)}"}, status=status.HTTP_404_NOT_FOUND
            )

        data = request.data.copy()
        data.pop("user_id", None)

        serializer = UserRegistrationStep2Serializer(user, data=data, partial=False)

        if serializer.is_valid():
            try:
                updated_user = serializer.save()
                return Response(
                    {
                        "message": "Registration completed successfully",
                        "user": UserAccountSerializer(updated_user).data,
                    },
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                return Response(
                    {"error": f"Error saving user: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return Response(
            {"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
        )

    def create(self, request, *args, **kwargs):

        return Response(
            {
                "message": "Please use the two-step registration endpoints: /register-step1/ and /register-step2/"
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
