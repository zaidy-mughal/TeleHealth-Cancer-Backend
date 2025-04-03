from rest_framework import serializers
from api.users.models import User  # Custom user model
from .models import Patient
from django.core.exceptions import ValidationError


def register_user(username, password, **extra_fields):
    if User.objects.filter(username=username).exists():
        raise ValidationError("A user with this username already exists.")
    user = User.objects.create_user(
        username=username, password=password, **extra_fields
    )
    return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]
        read_only_fields = ["id"]


class PatientSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Patient
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class PatientRegistrationSerializer(serializers.Serializer):
    # Define choices directly in the serializer
    SMOKING_FREQUENCY_CHOICES = [
        ("NEVER", "Never"),
        ("FORMER", "Former"),
        ("OCCASIONAL", "Occasional"),
        ("DAILY", "Daily"),
    ]

    ALCOHOL_FREQUENCY_CHOICES = [
        ("NEVER", "Never"),
        ("OCCASIONAL", "Occasional"),
        ("MODERATE", "Moderate"),
        ("HEAVY", "Heavy"),
    ]

    # User account fields
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, style={"input_type": "password"})

    # Patient fields
    first_name = serializers.CharField(max_length=100)
    middle_name = serializers.CharField(max_length=100, required=False, allow_null=True)
    last_name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    phone_number = serializers.CharField(max_length=20)
    address = serializers.CharField(max_length=255)
    state = serializers.CharField(max_length=100)
    city = serializers.CharField(max_length=100)
    zipcode = serializers.CharField(max_length=20)

    # Medical professional information
    physician_name = serializers.CharField(
        max_length=255, required=False, allow_null=True
    )
    physician_contact_number = serializers.CharField(
        max_length=20, required=False, allow_null=True
    )
    pharmacist_name = serializers.CharField(
        max_length=255, required=False, allow_null=True
    )
    pharmacist_contact_number = serializers.CharField(
        max_length=20, required=False, allow_null=True
    )

    # Visit type and cancer information
    visit_type = serializers.ChoiceField(choices=Patient.VISIT_TYPES)
    cancer_type = serializers.ChoiceField(
        choices=Patient.CANCER_TYPES, required=False, allow_null=True
    )
    cancer_duration = serializers.ChoiceField(
        choices=Patient.CANCER_DURATION_CHOICES, required=False, allow_null=True
    )

    # Smoking and Alcohol history with custom choices
    smoking_history = serializers.ChoiceField(
        choices=SMOKING_FREQUENCY_CHOICES, required=False, allow_null=True
    )
    alcohol_history = serializers.ChoiceField(
        choices=ALCOHOL_FREQUENCY_CHOICES, required=False, allow_null=True
    )

    def validate_email(self, value):
        if Patient.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "A patient with this email already exists."
            )
        return value

    def create(self, validated_data):
        # Extract user data
        user_data = {
            "username": validated_data.pop("username"),
            "password": validated_data.pop("password"),
            "email": validated_data.get("email"),
            "first_name": validated_data.get("first_name"),
            "last_name": validated_data.get("last_name"),
        }

        # Create User instance
        user = register_user(**user_data)

        # Remove smoking_history and alcohol_history if they're not in Patient model
        if "smoking_history" in validated_data and not hasattr(
            Patient, "smoking_history"
        ):
            validated_data.pop("smoking_history")

        if "alcohol_history" in validated_data and not hasattr(
            Patient, "alcohol_history"
        ):
            validated_data.pop("alcohol_history")

        # Create Patient instance
        patient = Patient.objects.create(user=user, **validated_data)

        return patient

    def to_representation(self, instance):
        return PatientSerializer(instance).data
