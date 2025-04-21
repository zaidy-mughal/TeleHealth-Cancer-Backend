from rest_framework import serializers

from api.patients.models import (
    Patient, IodineAllergy, Allergy, Medication, MedicalHistory,
    AddictionHistory, SurgicalHistory, CancerHistory, CancerType,
    Pharmacist, PrimaryPhysician, MaritalStatus
)


class IodineAllergySerializer(serializers.ModelSerializer):
    class Meta:
        model = IodineAllergy
        fields = ["is_allergic"]


class AllergySerializer(serializers.ModelSerializer):
    class Meta:
        model = Allergy
        fields = ["name"]


class MedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication
        fields = ["name"]


class MedicalHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalHistory
        fields = ["medical_condition"]


class SurgicalHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SurgicalHistory
        fields = ["surgical_condition"]


class PrimaryPhysicianSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrimaryPhysician
        fields = ["name", "contact_number"]


class PharmacistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pharmacist
        fields = ["name", "contact_number"]


class CancerTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CancerType
        fields = ["name"]


class CancerHistorySerializer(serializers.ModelSerializer):
    cancer_type = CancerTypeSerializer()

    class Meta:
        model = CancerHistory
        fields = ["cancer_type", "year_of_diagnosis", "treatment_received"]


class AddictionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AddictionHistory
        fields = ["addiction_type", "description", "total_years"]


class PatientSerializer(serializers.ModelSerializer):
    allergies = AllergySerializer(many=True, required=True)
    medications = MedicationSerializer(many=True, required=True)
    medical_history = MedicalHistorySerializer(many=True, required=True)
    surgical_history = SurgicalHistorySerializer(many=True, required=True)
    primary_physician = PrimaryPhysicianSerializer(required=True)
    pharmacist = PharmacistSerializer(required=True)
    cancer_history = CancerHistorySerializer(many=True, required=True)
    addiction_history = AddictionHistorySerializer(many=True, required=True)

    class Meta:
        model = Patient
        fields = [
            "uuid", "gender", "marital_status", "sex_assign_at_birth",
            "state", "city", "zip_code", "allergies", "medications",
            "medical_history", "surgical_history", "primary_physician",
            "pharmacist", "cancer_history", "addiction_history",
        ]
        read_only_fields = ["uuid"]


    def validate(self, attrs):
        missing = [field for field in self.fields if field not in self.initial_data and field not in self.Meta.read_only_fields]
        if missing:
            raise serializers.ValidationError({
                field: "This field is required in the payload." for field in missing
            })
        return super().validate(attrs)



    def update(self, instance, validated_data):
        # Primary Physician
        primary_physician_data = validated_data.pop("primary_physician")
        primary_physician, _ = PrimaryPhysician.objects.get_or_create(
            **primary_physician_data
        )
        instance.primary_physician = primary_physician

        # Pharmacist
        pharmacist_data = validated_data.pop("pharmacist")
        pharmacist, _ = Pharmacist.objects.get_or_create(**pharmacist_data)
        instance.pharmacist = pharmacist

        # Update simple fields directly
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        # M2M fields
        allergies = validated_data.pop("allergies")
        instance.allergies.set(
            [Allergy.objects.get_or_create(**item)[0] for item in allergies]
        )

        medications = validated_data.pop("medications")
        instance.medications.set(
            [Medication.objects.get_or_create(**item)[0] for item in medications]
        )

        medical_history = validated_data.pop("medical_history")
        instance.medical_history.set(
            [
                MedicalHistory.objects.get_or_create(**item)[0]
                for item in medical_history
            ]
        )

        surgical_history = validated_data.pop("surgical_history")
        instance.surgical_history.set(
            [
                SurgicalHistory.objects.get_or_create(**item)[0]
                for item in surgical_history
            ]
        )

        # Cancer History
        cancer_history = validated_data.pop("cancer_history")
        instance.cancer_history.all().delete()
        for cancer_data in cancer_history:
            cancer_type_data = cancer_data.pop("cancer_type")
            cancer_type, _ = CancerType.objects.get_or_create(**cancer_type_data)
            CancerHistory.objects.create(
                patient=instance, cancer_type=cancer_type, **cancer_data
            )

        # Addiction History
        addiction_history = validated_data.pop("addiction_history")
        instance.addiction_history.all().delete()
        for addiction_data in addiction_history:
            AddictionHistory.objects.create(patient=instance, **addiction_data)

        return instance

    # will utilize it if i need a seperate api to create patient only
    def create(self, validated_data):
        pass
