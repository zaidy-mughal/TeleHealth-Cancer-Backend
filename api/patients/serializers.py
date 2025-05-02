from rest_framework import serializers

from api.patients.models import (
    Patient,
    IodineAllergy,
    Allergy,
    Medication,
    MedicalHistory,
    AddictionHistory,
    SurgicalHistory,
    CancerHistory,
    CancerType,
    Pharmacist,
    PrimaryPhysician,
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
    
    surgical_history = SurgicalHistorySerializer(many=True, allow_empty=True)
    cancer_history = CancerHistorySerializer(many=True, allow_empty=True)
    addiction_history = AddictionHistorySerializer(many=True, allow_empty=True)

    primary_physician = PrimaryPhysicianSerializer(allow_blank=False)
    pharmacist = PharmacistSerializer(allow_blank=False)
    iodine_allergy = IodineAllergySerializer(allow_blank=False)
    allergies = AllergySerializer(many=True, allow_empty=False)
    medications = MedicationSerializer(many=True, allow_empty=False)
    medical_history = MedicalHistorySerializer(many=True, allow_empty=False)

    class Meta:
        model = Patient
        fields = [
            "uuid",
            "gender",
            "marital_status",
            "sex_assign_at_birth",
            "state",
            "city",
            "zip_code",
            "visit_type",
            "allergies",
            "iodine_allergy",
            "medications",
            "medical_history",
            "surgical_history",
            "primary_physician",
            "pharmacist",
            "cancer_history",
            "addiction_history",
        ]
        read_only_fields = ["uuid"]

    def validate(self, attrs):
        missing = [
            field
            for field in self.fields
            if field not in attrs and field not in self.Meta.read_only_fields
        ]
        if missing:
            raise serializers.ValidationError(
                {field: "This field is required in the payload." for field in missing}
            )
        return super().validate(attrs)

    def update(self, instance, validated_data):
        try:
            print("Updating patient instance:", instance)

            # First, extract all the many-to-many fields before saving
            allergies_data = validated_data.pop("allergies")
            medications_data = validated_data.pop("medications")
            medical_history_data = validated_data.pop("medical_history")
            surgical_history_data = validated_data.pop("surgical_history")
            cancer_history_data = validated_data.pop("cancer_history")
            addiction_history_data = validated_data.pop("addiction_history")

            # adding one to one field
            iodine_allergy_data = validated_data.pop("iodine_allergy")
            iodine_allergy, _ = IodineAllergy.objects.get_or_create(
                patient=instance,
                defaults={"is_allergic": iodine_allergy_data.get("is_allergic", False)},
            )
            iodine_allergy.is_allergic = iodine_allergy_data.get("is_allergic", False)
            iodine_allergy.save()

            # Handle the foreign key fields
            primary_physician_data = validated_data.pop("primary_physician")
            primary_physician, _ = PrimaryPhysician.objects.get_or_create(
                **primary_physician_data
            )
            instance.primary_physician = primary_physician

            pharmacist_data = validated_data.pop("pharmacist")
            pharmacist, _ = Pharmacist.objects.get_or_create(**pharmacist_data)
            instance.pharmacist = pharmacist

            # Update simple fields directly
            for attr, value in validated_data.items():
                setattr(instance, attr, value)

            instance.save()

            # Now handle M2M fields AFTER saving the instance
            instance.allergies.set(
                [Allergy.objects.get_or_create(**item)[0] for item in allergies_data]
            )

            instance.medications.set(
                [
                    Medication.objects.get_or_create(**item)[0]
                    for item in medications_data
                ]
            )

            instance.medical_history.set(
                [
                    MedicalHistory.objects.get_or_create(**item)[0]
                    for item in medical_history_data
                ]
            )

            instance.surgical_history.set(
                [
                    SurgicalHistory.objects.get_or_create(**item)[0]
                    for item in surgical_history_data
                ]
            )

            # Cancer History
            instance.cancer_history.all().delete()
            for cancer_data in cancer_history_data:
                cancer_type_data = cancer_data.pop("cancer_type")
                cancer_type, _ = CancerType.objects.get_or_create(**cancer_type_data)
                CancerHistory.objects.create(
                    patient=instance, cancer_type=cancer_type, **cancer_data
                )

            # Addiction History
            instance.addiction_history.all().delete()
            for addiction_data in addiction_history_data:
                AddictionHistory.objects.create(patient=instance, **addiction_data)
            print("Addiction History updated")
        except (Exception, serializers.ValidationError) as e:
            raise serializers.ValidationError(f"Failed to update patient: {str(e)}")

        return instance

    # will utilize it if i need a seperate api to create patient only
    # patient is created when user is created automatically
    def create(self, validated_data):
        pass
