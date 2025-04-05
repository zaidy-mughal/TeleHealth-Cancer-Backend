from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer
from api.users.models import User
from api.patients.models import Patient


class CustomRegisterSerializer(RegisterSerializer):
    fullname = serializers.CharField(required=True)
    date_of_birth = serializers.DateField(required=True)
    gender = serializers.ChoiceField(choices=[("Male", "Male"), ("Female", "Female")])
    visit_type = serializers.CharField(required=True)
    username = None  # Remove username field

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data["fullname"] = self.validated_data.get("fullname", "")
        data["date_of_birth"] = self.validated_data.get("date_of_birth")
        data["gender"] = self.validated_data.get("gender", "")
        data["visit_type"] = self.validated_data.get("visit_type", "")
        return data

    def custom_signup(self, request, user):
        # Split fullname into first and last names
        fullname = self.validated_data.get("fullname", "")
        if fullname:
            names = fullname.split(" ", 1)
            user.first_name = names[0]
            user.last_name = names[1] if len(names) > 1 else ""

        try:
            user.save()

            Patient.objects.create(
                user=user,
                date_of_birth=self.validated_data.get("date_of_birth"),
                gender=self.validated_data.get("gender"),
                visit_type=self.validated_data.get("visit_type"),
            )
        except Exception as e:
            user.delete()
            raise serializers.ValidationError(
                {"detail": f"Failed to create Patient profile: {str(e)}"}
            )


class CustomLoginSerializer(LoginSerializer):
    username = None  # Remove the username
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        return super().validate(attrs)
