from typing import override

from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer
from api.users.models import User
from api.patients.models import Patient
from api.authentication.validators import (
    validate_email_not_exits,
    validate_dob_not_in_future,
)


class TeleHealthRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    date_of_birth = serializers.DateField(required=True)
    phone_number = serializers.CharField(required=True)
    username = None  # Remove username field

    def validate_email(self, email):
        return validate_email_not_exits(self,email)

    def validate_date_of_birth(self, dob):
        return validate_dob_not_in_future(self,dob)

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data["first_name"] = self.validated_data.get("first_name", "")
        data["last_name"] = self.validated_data.get("last_name", "")
        data["date_of_birth"] = self.validated_data.get("date_of_birth")
        data["phone_number"] = self.validated_data.get("phone_number", "")
        return data

    @override
    def custom_signup(self, request, user):        
        
        user.first_name = self.validated_data.get("first_name", "")
        user.last_name = self.validated_data.get("last_name", "")
        role = self.validated_data.get("role", None)
        if role:
            user.role = role

        try:
            user.save()

            Patient.objects.create(
                user=user,
                date_of_birth=self.validated_data.get("date_of_birth"),
                phone_number=self.validated_data.get("phone_number"),
            )
        except Exception as e:
            user.delete()
            raise serializers.ValidationError(
                {"detail": f"Failed to create Patient profile: {str(e)}"}
            )


class TeleHealthLoginSerializer(LoginSerializer):
    username = None  # Remove the username
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        data = super().validate(attrs)
        data['role'] = data.get('user').role
        return data
