from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer, PasswordResetSerializer
from api.users.models import User
from api.patients.models import Patient
from api.authentication.utilities.otp import create_otp_for_user
from api.authentication.utilities.send_email import send_otp_email
from api.authentication.validators import (
    validate_email_not_exits,
    validate_dob_not_in_future,
    validate_otp_for_email,
)


class TeleHealthRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True, allow_blank=True)
    date_of_birth = serializers.DateField(required=True)
    phone_number = serializers.CharField(required=True)
    username = serializers.CharField(required=False)  # Make username optional

    def validate_email(self, email):
        return validate_email_not_exits(self, email)

    def validate_date_of_birth(self, dob):
        return validate_dob_not_in_future(self, dob)

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data["first_name"] = self.validated_data.get("first_name", "")
        data["last_name"] = self.validated_data.get("last_name", "")
        data["date_of_birth"] = self.validated_data.get("date_of_birth")
        data["phone_number"] = self.validated_data.get("phone_number", "")
        # Generate username from email if not provided
        if not data.get("username"):
            data["username"] = self.validated_data.get("email").split("@")[0]
        return data

    def custom_signup(self, request, user):
        user.first_name = self.validated_data.get("first_name", "")
        user.last_name = self.validated_data.get("last_name", "")
        role = self.validated_data.get("role", None)
        if role:
            user.role = role

        try:
            user.save()

            patient = Patient.objects.create(
                user=user,
                date_of_birth=self.validated_data.get("date_of_birth"),
                phone_number=self.validated_data.get("phone_number"),
                is_iodine_contrast_allergic=False
            )

            # Create IodineAllergy record with default value
            from api.patients.models import IodineAllergy
            IodineAllergy.objects.create(
                patient=patient,
                is_allergic=False
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
        data["role"] = data.get("user").role
        return data


class OTPPasswordResetSerializer(PasswordResetSerializer):
    """
    Serializer for requesting a password reset via OTP instead of email link.
    """

    email = serializers.EmailField(required=True)

    def save(self):

        try:
            email = self.validated_data["email"].lower()
            user = User.objects.get(email=email)

            otp_obj = create_otp_for_user(user)

            send_otp_email(user, otp_obj.otp)

        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"detail": "User with this email does not exist."}
            )


class OTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6, min_length=6)

    def validate(self, attrs):
        email = attrs.get("email").lower()
        otp = attrs.get("otp")

        try:
            is_valid, otp_obj = validate_otp_for_email(email, otp)
            if not is_valid:
                raise serializers.ValidationError("Invalid or expired OTP")

            otp_obj.is_used = True
            otp_obj.save()

        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email address")

        return attrs
