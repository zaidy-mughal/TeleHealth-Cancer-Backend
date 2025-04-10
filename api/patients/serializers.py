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
from api.users.serializers import UserSerializer
from api.users.models import User


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


class PatientSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    
    allergies = AllergySerializer(many=True, write_only=True, required=False)
    medications = MedicationSerializer(many=True, write_only=True, required=False)
    medical_history = MedicalHistorySerializer(many=True, write_only=True, required=False)
    surgical_history = SurgicalHistorySerializer(many=True, write_only=True, required=False)
    cancer_history = CancerHistorySerializer(many=True, write_only=True, required=False)
    addiction_history = AddictionSerializer(many=True, write_only=True, required=False)
    primary_physician = PrimaryPhysicianSerializer(many=True, write_only=True, required=False)
    pharmacist = PharmacistSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = Patient
        fields = [
            "uuid", "user", "visit_type", "marital_status", "sex_assign_at_birth",
            "state", "city", "zip_code", "is_iodine_contrast_allergic",
            "allergies", "medications", "medical_history", "surgical_history",
            "cancer_history", "addiction_history", "primary_physician", "pharmacist"
        ]
        read_only_fields = ["uuid"]

    def create(self, validated_data):
        # Pop out nested fields and create objects after patient creation
        nested_data = {
            "allergies": validated_data.pop("allergies", []),
            "medications": validated_data.pop("medications", []),
            "medical_history": validated_data.pop("medical_history", []),
            "surgical_history": validated_data.pop("surgical_history", []),
            "cancer_history": validated_data.pop("cancer_history", []),
            "addiction_history": validated_data.pop("addiction_history", []),
            "primary_physician": validated_data.pop("primary_physician", []),
            "pharmacist": validated_data.pop("pharmacist", []),
        }

        patient = Patient.objects.create(**validated_data)

        # Create nested objects
        for model_name, entries in nested_data.items():
            model_class = self.fields[model_name].child.Meta.model      #used to get the model class
            for item in entries:
                model_class.objects.create(patient=patient, **item)

        return patient
