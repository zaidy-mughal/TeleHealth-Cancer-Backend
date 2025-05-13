from datetime import date
from rest_framework import serializers
from django.db import transaction
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer, PasswordResetSerializer
from rest_framework_simplejwt.tokens import RefreshToken


from api.users.models import User
from api.users.choices import Role
from api.patients.models import Patient
from api.doctors.models import Doctor, Specialization, Service, DoctorService
from api.authentication.utilities.otp import create_otp_for_user
from api.authentication.utilities.send_email import send_otp_email
from api.authentication.validators import (
    validate_email_not_exits,
    validate_dob_not_in_future,
    validate_otp_for_email,
    validate_password_match,
    validate_email_otp_verified,
    validate_email_exits,
    validate_min_length,
    validate_special_character,
    validate_uppercase,
    validate_email_format,
    validate_name_length,
    validate_doctor_fields,
    validate_patient_fields,
)


class TeleHealthRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True, allow_blank=True)
    username = None
    role = serializers.IntegerField(required=False)

    # Patient-specific fields
    date_of_birth = serializers.DateField(required=True)
    phone_number = serializers.CharField(required=False)
    profile_uuid = serializers.UUIDField(read_only=True)

    # Doctor-specific fields
    specialization = serializers.CharField(required=False)
    npi_number = serializers.CharField(required=False)
    address = serializers.CharField(required=False)
    service = serializers.IntegerField(required=False)


    def validate_email(self, email):
        return validate_email_not_exits(self, email)
    
    def validate_password1(self, password):
        validate_uppercase(password)
        validate_special_character(password)
        validate_min_length(password)
        return password

    def validate_date_of_birth(self, dob):
        return validate_dob_not_in_future(self, dob)

    def validate(self, data):
        validate_email_format(self, data)
        validate_password_match(self, data)
        validate_name_length(self, data)

        if data.get("role") == 1:
            validate_doctor_fields(self, data)
        else:
            validate_patient_fields(self, data)

        return data

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data["first_name"] = self.validated_data.get("first_name", "")
        data["last_name"] = self.validated_data.get("last_name", "")
        data["role"] = self.validated_data.get("role")

        # Patient-specific fields
        data["date_of_birth"] = self.validated_data.get("date_of_birth")
        data["phone_number"] = self.validated_data.get("phone_number", "")

        # Doctor-specific fields
        data["specialization"] = self.validated_data.get("specialization", "")
        data["npi_number"] = self.validated_data.get("npi_number", "")
        data["address"] = self.validated_data.get("address", "")
        data["service"] = self.validated_data.get("service", "")

        return data

    @transaction.atomic
    def custom_signup(self, request, user):
        user.first_name = self.validated_data.get("first_name", "")
        user.last_name = self.validated_data.get("last_name", "")
        role = self.validated_data.get("role")
        if role is not None:
            user.role = role
        user.save()

        if user.role == Role.PATIENT:
            try:
                patient = Patient.objects.create(
                    user=user,
                    date_of_birth=self.validated_data.get("date_of_birth"),
                    phone_number=self.validated_data.get("phone_number"),
                )
                self.profile_uuid = patient.uuid

            except Exception as e:
                raise serializers.ValidationError(
                    {"detail": f"Failed to create profile: {str(e)}"}
                )
        
        elif user.role == Role.DOCTOR:
            try:
                specialization, _ = Specialization.objects.get_or_create(
                    name=self.validated_data.get("specialization")
                )
                doctor = Doctor.objects.create(
                    user=user,
                    specialization=specialization,
                    npi_number=self.validated_data.get("npi_number"),
                    address=self.validated_data.get("address"),
                    date_of_birth=self.validated_data.get("date_of_birth"),
                )
                service = self.validated_data.get("service")
                if service not in (0, 1, 2, 3):
                    raise serializers.ValidationError(
                        {"service": "Invalid service ID."}
                    )
                service_obj, _ = Service.objects.get_or_create(name=service)
                DoctorService.objects.create(
                    doctor=doctor, service=service_obj
                )
                self.profile_uuid = doctor.uuid

            except Exception as e:
                raise serializers.ValidationError(
                    {"detail": f"Failed to create profile: {str(e)}"}
                )
        else:
            raise serializers.ValidationError(
                {"role": "Role must be 2 (Patient) OR 1 (Doctor)."}
            )
        


class TeleHealthLoginSerializer(LoginSerializer):
    username = None  # Remove the username
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        data = super().validate(attrs)
        user = data.get("user")
        data["role"] = user.role
        profile_uuid = None

        try:
            if user.role == 0:
                user = User.objects.get(email=self.validated_data["email"])
                profile_uuid = user.uuid

            elif user.role == 1:
                doctor = Doctor.objects.get(user=user)
                profile_uuid = doctor.uuid

            elif user.role == 2:
                patient = Patient.objects.get(user=user)
                profile_uuid = patient.uuid
            

        except Exception as e:
            raise serializers.ValidationError(
                {"detail": f"Error Logging in {e}."}
            )
                
        data["profile_uuid"] = profile_uuid
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
        
        except Exception as e:
            raise serializers.ValidationError(
                {"detail": f"Failed to send OTP: {str(e)}"}
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
        
        except Exception as e:
            raise serializers.ValidationError(
                {"detail": f"Failed to verify OTP: {str(e)}"}
            )

        return attrs


class PasswordChangeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    new_password1 = serializers.CharField(min_length=8, required=True)
    new_password2 = serializers.CharField(min_length=8, required=True)

    def validate_email(self, email):
        exist = validate_email_exits(self, email)
        if not exist:
            raise serializers.ValidationError(
                {"email": "User with this email does not exist."}
            )

        self.user = User.objects.get(email=email.lower())
        verified_otp = validate_email_otp_verified(self, self.user)
        if not verified_otp:
            raise serializers.ValidationError(
                {"email": "You must verify your OTP before changing password"}
            )

        return email

    def validate(self, data):
        validate_password_match(self, data)
        return data

    def save(self):
        new_password = self.validated_data["new_password1"]

        try:
            self.user.set_password(new_password)
            self.user.save()
            return self.user
        except Exception as e:
            raise serializers.ValidationError(
                {"detail": f"Failed to change password: {str(e)}"}
            )


# Custom Logout Serializer to bypass the default dj-rest-auth logout
class TeleHealthLogoutSerializer(serializers.Serializer):
    """
    Serializer for logging out a user.
    """

    refresh = serializers.CharField()

    def validate_refresh(self, value):
        try:
            RefreshToken(value)
            return value
        except Exception as e:
            raise serializers.ValidationError("Invalid refresh token")

    def save(self):
        try:
            refresh_token = self.validated_data["refresh"]

            # Blacklist the token
            token = RefreshToken(refresh_token)
            token.blacklist()

        except Exception as e:
            raise serializers.ValidationError(f"Failed to blacklist token: {str(e)}")
