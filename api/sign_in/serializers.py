from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from api.users.models import User  # Custom User model
from .models import UserAccount
from django.db import transaction
from api.patients.models import Patient
from api.appointments.models import Doctor


class RoleBasedRegistrationSerializer(serializers.ModelSerializer):

    confirm_password = serializers.CharField(write_only=True, required=True)
    role = serializers.ChoiceField(
        choices=["PATIENT", "DOCTOR"], write_only=True, required=True
    )

    class Meta:
        model = UserAccount
        fields = ["full_name", "email", "password", "confirm_password", "role"]
        extra_kwargs = {
            "full_name": {"required": True},
            "email": {"required": True},
            "password": {"write_only": True, "required": True},
        }

    def validate(self, data):
        password = data.get("password")
        confirm_password = data.pop("confirm_password", None)
        if password != confirm_password:
            raise serializers.ValidationError(
                {"confirm_password": "Password and confirm password do not match."}
            )

        email = data.get("email")
        if UserAccount.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {"email": "A user with this email already exists."}
            )
        return data

    @transaction.atomic
    def create(self, validated_data):
        # Pop and save role separately to use it later.
        role = validated_data.pop("role", None)

        email = validated_data["email"]
        username = self._generate_unique_username(email)

        # Create the Django user
        user = User.objects.create_user(
            username=username, email=email, password=validated_data["password"]
        )

        # Encrypt the password for the UserAccount model
        validated_data["password"] = make_password(validated_data["password"])
        user_account = UserAccount.objects.create(**validated_data)

        # Assign the Django user and role to the user_account and save
        user_account.django_user = user
        user_account.role = role  # Assign the role here
        user_account.save()

        # Create related model based on the role
        if role == "PATIENT":
            Patient.objects.create(
                user=user,
                first_name=validated_data["full_name"].split()[0],
                last_name=(
                    " ".join(validated_data["full_name"].split()[1:])
                    if len(validated_data["full_name"].split()) > 1
                    else ""
                ),
                email=email,
            )
        elif role == "DOCTOR":
            Doctor.objects.create(user=user, name=validated_data["full_name"])

        return user_account

    def _generate_unique_username(self, email):
        base_username = email.split("@")[0]
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1
        return username


class UserRegistrationStep2Serializer(serializers.ModelSerializer):

    date_of_birth = serializers.DateField(input_formats=["%m-%d-%Y"], required=True)

    class Meta:
        model = UserAccount
        fields = [
            "date_of_birth",
            "gender",
            "visit_type",
        ]
        extra_kwargs = {
            "date_of_birth": {"required": True},
            "gender": {"required": True},
            "visit_type": {"required": True},
        }


class UserAccountSerializer(serializers.ModelSerializer):

    date_of_birth = serializers.DateField(input_formats=["%m-%d-%Y"], required=True)

    class Meta:
        model = UserAccount
        fields = [
            "id",
            "full_name",
            "email",
            "date_of_birth",
            "gender",
            "visit_type",
            "created_at",
        ]
        extra_kwargs = {
            "created_at": {"read_only": True},
        }


class UserAccountUpdateSerializer(serializers.ModelSerializer):

    date_of_birth = serializers.DateField(input_formats=["%m-%d-%Y"], required=False)

    password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = UserAccount
        fields = [
            "full_name",
            "email",
            "password",
            "confirm_password",
            "date_of_birth",
            "gender",
            "visit_type",
        ]
        extra_kwargs = {
            "full_name": {"required": False},
            "email": {"required": False},
            "gender": {"required": False},
            "visit_type": {"required": False},
        }

    def validate(self, data):

        password = data.get("password")
        confirm_password = (
            data.pop("confirm_password", None) if "confirm_password" in data else None
        )

        if password and confirm_password and password != confirm_password:
            raise serializers.ValidationError(
                "Password and confirm password do not match."
            )

        return data

    def update(self, instance, validated_data):

        if "password" in validated_data:
            validated_data["password"] = make_password(validated_data["password"])
        return super().update(instance, validated_data)
