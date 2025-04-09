from rest_framework import serializers
from .models import (
    Patient,
    Allergy,
    Medication,
    MedicalHistory,
    SurgicalHistory,
    CancerType,
    CancerHistory,
    Pharmacist,
    PrimaryPhysician,
    Addiction,
)
from users.serializers import UserSerializer
from users.models import User


class PatientSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Patient
        fields = [
            "uuid",
            "user",
            "visit_type",
            "marital_status",
            "sex_assign_at_birth",
            "state",
            "city",
            "zip_code",
            "is_iodine_contrast_allergic",
        ]
        read_only_fields = ["uuid"]


class AllergySerializer(serializers.ModelSerializer):
    """
    Serializer for the Allergy model.
    """

    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())

    class Meta:
        model = Allergy
        fields = "__all__"


class MedicationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Medication model.
    """

    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())

    class Meta:
        model = Medication
        fields = "__all__"


class MedicalHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Medical History model.
    """

    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())

    class Meta:
        model = MedicalHistory
        fields = "__all__"


class SurgicalHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Surgical History model.
    """

    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())

    class Meta:
        model = SurgicalHistory
        fields = "__all__"


class CancerTypeSerializer(serializers.ModelSerializer):
    """
    Serializer for the CancerType model.
    """

    class Meta:
        model = CancerType
        fields = "__all__"


class CancerHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for the CancerHistory model.
    """

    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    cancer_type = serializers.PrimaryKeyRelatedField(queryset=CancerType.objects.all())

    class Meta:
        model = CancerHistory
        fields = "__all__"


class PharmacistSerializer(serializers.ModelSerializer):
    """
    Serializer for the Pharmacist model.
    """

    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())

    class Meta:
        model = Pharmacist
        fields = "__all__"


class PrimaryPhysicianSerializer(serializers.ModelSerializer):
    """
    Serializer for the PrimaryPhysician model.
    """

    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())

    class Meta:
        model = PrimaryPhysician
        fields = "__all__"


class AddictionSerializer(serializers.ModelSerializer):
    """
    Serializer for the Addiction model.
    """

    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())

    class Meta:
        model = Addiction
        fields = "__all__"
