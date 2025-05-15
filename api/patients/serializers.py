from attr import validate
from rest_framework import serializers
from django.db import transaction

from api.patients.models import (
    Patient,
    IodineAllergy,
    Allergy,
    Medication,
    MedicalHistory,
    SurgicalHistory,
    CancerType,
    CancerHistory,
    TreatmentRecieved,
    AddictionHistory,
    CareProvider,
    PatientAllergy,
    PatientMedication,
    PatientMedicalHistory,
    PatientSurgicalHistory,
    PatientCareProvider,
)
from api.patients.validators import validate_fields


class IodineAllergySerializer(serializers.ModelSerializer):
    print('iodine allergy serializer')
    is_iodine_allergic = serializers.IntegerField(required=True)

    class Meta:
        model = IodineAllergy
        fields = ["id", "uuid", "is_iodine_allergic"]


class AllergySerializer(serializers.ModelSerializer):
    class Meta:
        model = Allergy
        fields = ["id", "uuid", "name"]


class MedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication
        fields = ["id", "uuid", "name"]


class MedicalHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalHistory
        fields = ["id", "uuid", "medical_condition"]


class SurgicalHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SurgicalHistory
        fields = ["id", "uuid", "surgical_condition"]


class CareProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = CareProvider
        fields = ["id", "uuid", "name", "contact_number"]


class CancerTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CancerType
        fields = ["id", "uuid", "name"]



class TreatmentReceivedSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreatmentRecieved
        fields = ["id", "uuid", "name"]


class CancerHistorySerializer(serializers.ModelSerializer):
    cancer_type = CancerTypeSerializer()
    treatment_received = TreatmentReceivedSerializer(many=True)

    class Meta:
        model = CancerHistory
        fields = [
            "id",
            "uuid",
            "cancer_type",
            "year_of_diagnosis",
            "treatment_received",
        ]




class AddictionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AddictionHistory
        fields = ["id", "uuid", "addiction_type", "total_years"]


class PatientSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)

    surgical_histories = SurgicalHistorySerializer(many=True, allow_empty=True, default=list)
    cancer_history = CancerHistorySerializer(many=True, allow_empty=True, default=list)
    addiction_history = AddictionHistorySerializer(many=True, allow_empty=True, default=list)

    iodine_allergy = IodineAllergySerializer()
    allergies = AllergySerializer(many=True, allow_empty=True, default=list)
    medications = MedicationSerializer(many=True, allow_empty=True, default=list)
    medical_histories = MedicalHistorySerializer(many=True, allow_empty=True, default=list)
    care_providers = CareProviderSerializer(many=True, allow_empty=True, default=list)

    class Meta:
        model = Patient
        fields = [
            "id",
            "uuid",
            "email",
            "first_name",
            "last_name",
            "date_of_birth",
            "gender",
            "phone_number",
            "visit_type",
            "marital_status",
            "sex_assigned_at_birth",
            "state",
            "city",
            "zip_code",
            "iodine_allergy",
            "allergies",
            "medications",
            "medical_histories",
            "surgical_histories",
            "care_providers",
            "cancer_history",
            "addiction_history",
        ]
        read_only_fields = ["id", "uuid", "email", "first_name", "last_name"]

    def validate(self, attrs):
        validate_fields(self, attrs)
        return super().validate(attrs)


    @transaction.atomic
    def update(self, instance, validated_data):
        try:
            allergies_data = validated_data.pop("allergies", None)
            medications_data = validated_data.pop("medications", None)
            medical_histories_data = validated_data.pop("medical_histories", None)
            surgical_histories_data = validated_data.pop("surgical_histories", None)
            care_providers_data = validated_data.pop("care_providers", None)
            cancer_history_data = validated_data.pop("cancer_history", None)
            addiction_history_data = validated_data.pop("addiction_history", None)
            iodine_allergy_data = validated_data.pop("iodine_allergy")

            # Update Iodine Allergy 1:1
            if iodine_allergy_data:
                iodine_allergy, _ = IodineAllergy.objects.get_or_create(
                    patient=instance,
                    defaults={
                        "is_iodine_allergic": iodine_allergy_data.get(
                            "is_iodine_allergic", False
                        )
                    },
                )
                iodine_allergy.is_iodine_allergic = iodine_allergy_data.get(
                    "is_iodine_allergic", False
                )
                iodine_allergy.save()
            
            # Update patient information
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()


            # Handle all many-to-many relationships M:M
            if allergies_data is not None:
                PatientAllergy.objects.filter(patient=instance).delete()

                for allergy_data in allergies_data:
                    allergy, _ = Allergy.objects.get_or_create(
                        name=allergy_data["name"]
                    )
                    PatientAllergy.objects.create(patient=instance, allergy=allergy)

            if medications_data is not None:
                PatientMedication.objects.filter(patient=instance).delete()

                for medication_data in medications_data:
                    medication, _ = Medication.objects.get_or_create(
                        name=medication_data["name"]
                    )
                    PatientMedication.objects.create(
                        patient=instance, medication=medication
                    )

            if medical_histories_data is not None:
                PatientMedicalHistory.objects.filter(patient=instance).delete()

                for medical_history_data in medical_histories_data:
                    medical_history, _ = MedicalHistory.objects.get_or_create(
                        medical_condition=medical_history_data["medical_condition"]
                    )
                    PatientMedicalHistory.objects.create(
                        patient=instance, medical_history=medical_history
                    )

            if surgical_histories_data is not None:
                PatientSurgicalHistory.objects.filter(patient=instance).delete()

                for surgical_history_data in surgical_histories_data:
                    surgical_history, _ = SurgicalHistory.objects.get_or_create(
                        surgical_condition=surgical_history_data["surgical_condition"]
                    )
                    PatientSurgicalHistory.objects.create(
                        patient=instance, surgical_history=surgical_history
                    )

            if care_providers_data is not None:
                PatientCareProvider.objects.filter(patient=instance).delete()

                for care_provider_data in care_providers_data:
                    care_provider, _ = CareProvider.objects.get_or_create(
                        name=care_provider_data["name"],
                        contact_number=care_provider_data["contact_number"],
                        type=care_provider_data["type"],
                    )
                    PatientCareProvider.objects.create(
                        patient=instance, care_provider=care_provider
                    )

            # Now One to Many Relationship 1:M
            if cancer_history_data is not None:
                CancerHistory.objects.filter(patient=instance).delete()

                for cancer_data in cancer_history_data:
                    cancer_type_data = cancer_data.pop("cancer_type")
                    treatment_data = cancer_data.pop("treatment_received", [])

                    cancer_type, _ = CancerType.objects.get_or_create(**cancer_type_data)

                    cancer_history = CancerHistory.objects.create(
                        patient=instance,
                        cancer_type=cancer_type,
                        year_of_diagnosis=cancer_data["year_of_diagnosis"],
                    )

                    for treatment in treatment_data:
                        TreatmentRecieved.objects.create(
                            cancer_history=cancer_history,
                            name=treatment["name"]
                        )

            if addiction_history_data is not None:
                AddictionHistory.objects.filter(patient=instance).delete()

                for addiction_data in addiction_history_data:
                    AddictionHistory.objects.create(
                        patient=instance,
                        addiction_type=addiction_data["addiction_type"],
                        total_years=addiction_data["total_years"],
                    )


        except Exception as e:
            raise serializers.ValidationError({"error": str(e)})

        return instance

    # will utilize it if i need a seperate api to create patient only
    # but in requirements, the patient is created when user is created automatically
    def create(self, validated_data):
        pass


class PatientAllergySerializer(serializers.ModelSerializer):
    allergy = AllergySerializer()

    class Meta:
        model = PatientAllergy
        fields = ["id", "uuid", "patient", "allergy"]


class PatientMedicationSerializer(serializers.ModelSerializer):
    medication = MedicationSerializer()

    class Meta:
        model = PatientMedication
        fields = ["id", "uuid", "patient", "medication"]


class PatientMedicalHistorySerializer(serializers.ModelSerializer):
    medical_history = MedicalHistorySerializer()

    class Meta:
        model = PatientMedicalHistory
        fields = ["id", "uuid", "patient", "medical_history"]


class PatientSurgicalHistorySerializer(serializers.ModelSerializer):
    surgical_history = SurgicalHistorySerializer()

    class Meta:
        model = PatientSurgicalHistory
        fields = ["id", "uuid", "patient", "surgical_history"]


class PatientCareProviderSerializer(serializers.ModelSerializer):
    care_provider = CareProviderSerializer()

    class Meta:
        model = PatientCareProvider
        fields = ["id", "uuid", "patient", "care_provider"]
