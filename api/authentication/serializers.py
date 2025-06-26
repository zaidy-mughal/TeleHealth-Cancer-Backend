from django.db import transaction
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers


from api.users.models import User
from api.users.choices import Role
from api.patients.models import Patient
from api.patients.utils.fields import LabelChoiceField
from api.authentication.choices import Purpose
from api.doctors.choices import Services
from api.doctors.models import Doctor, Specialization, Service, DoctorService
from api.authentication.utilities.otp import create_otp_for_user
from api.services.send_email import EmailService
from api.authentication.validators import (
    validate_email_not_exits,
    validate_dob_not_in_future,
    validate_otp,
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
    validate_email_purpose_for_otp,
)


class TeleHealthRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True, allow_blank=True)
    username = None
    role = LabelChoiceField(choices=Role.choices, required=True)

    # Patient-specific fields
    date_of_birth = serializers.DateField(required=True)
    phone_number = serializers.CharField(required=False)
    profile_uuid = serializers.UUIDField(read_only=True)

    # Doctor-specific fields
    specialization = serializers.CharField(required=False)
    npi_number = serializers.CharField(required=False)
    address = serializers.CharField(required=False)
    service = LabelChoiceField(
        choices=Services.choices,
        required=False,
    )

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
        elif data.get("role") == 2:
            validate_patient_fields(self, data)
        else:
            raise serializers.ValidationError(
                {"role": "Role must be Patient OR Doctor."}
            )

        return data

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data["first_name"] = self.validated_data.get("first_name", "")
        data["last_name"] = self.validated_data.get("last_name", "")
        data["role"] = self.validated_data.get("role")

        data["date_of_birth"] = self.validated_data.get("date_of_birth")
        data["phone_number"] = self.validated_data.get("phone_number", "")

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
                medical_record = patient.medical_records.create(
                    is_main_record=True,
                )
                medical_record.save()
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
                DoctorService.objects.create(doctor=doctor, service=service_obj)
                self.profile_uuid = doctor.uuid

            except Exception as e:
                raise serializers.ValidationError(
                    {"detail": f"Failed to create profile: {str(e)}"}
                )
        else:
            raise serializers.ValidationError(
                {"role": "Role must be 2 (Patient) OR 1 (Doctor)."}
            )

        try:
            otp_obj = create_otp_for_user(user, purpose=Purpose.EMAIL_VERIFICATION)
            EmailService.send_otp_email(user, otp_obj.otp)
        except Exception as e:
            user.delete()
            raise serializers.ValidationError(
                {"detail": f"Failed to send verification OTP: {str(e)}"}
            )


class TeleHealthLoginSerializer(LoginSerializer):
    username = None  # Remove the username
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        data = super().validate(attrs)
        user = data.get("user")

        if not user.is_email_verified:
            raise serializers.ValidationError(
                {
                    "detail": "Please verify your email first. Check your inbox/spam for the verification OTP."
                }
            )

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
            raise serializers.ValidationError({"detail": f"Error Logging in {e}."})

        data["profile_uuid"] = profile_uuid

        return data


class RequestOTPSerializer(serializers.Serializer):
    """
    Generic serializer to request or resend OTP for any purpose.
    """

    email = serializers.EmailField()
    purpose = LabelChoiceField(choices=Purpose.choices, required=True)

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
            return value.lower()
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")

    def validate(self, attrs):
        email = attrs.get("email")
        purpose = attrs.get("purpose")

        try:
            user = User.objects.get(email=email)
            validate_email_purpose_for_otp(user, purpose)

        except User.DoesNotExist:
            raise serializers.ValidationError(
                {"email": "User with this email does not exist."}
            )

        return attrs

    def save(self):
        try:
            email = self.validated_data["email"]
            purpose = self.validated_data["purpose"]

            user = User.objects.get(email=email)

            otp_obj = create_otp_for_user(user, purpose=purpose)

            EmailService.send_otp_email(
                user=user,
                otp=otp_obj.otp,
            )

            return {"detail": f"One-time Passcode (OTP) has been sent to {email}."}

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
        purpose = self.context.get("purpose")

        try:
            is_valid, otp_obj = validate_otp(email, otp, purpose)
            if not is_valid:
                raise serializers.ValidationError("Invalid or expired OTP")

            otp_obj.is_used = True
            otp_obj.save()

            if purpose == Purpose.EMAIL_VERIFICATION:
                user = User.objects.get(email=email)
                user.is_email_verified = True
                user.save()

                try:
                    EmailService.send_welcome_email(user)

                except Exception as e:
                    raise serializers.ValidationError(
                        {"detail": f"Failed to send welcome email: {str(e)}"}
                    )

        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email address")

        except Exception as e:
            raise serializers.ValidationError(
                {"detail": f"Failed to verify OTP: {str(e)}"}
            )

        return attrs

    def save(self):
        return {"detail": "OTP verified successfully!", "verified": True}


class PasswordChangeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    new_password1 = serializers.CharField(min_length=8, required=True)
    new_password2 = serializers.CharField(min_length=8, required=True)

    def validate_email(self, email):
        validate_email_exits(self, email)

        user = User.objects.get(email=email.lower())
        validate_email_otp_verified(self, user)

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
