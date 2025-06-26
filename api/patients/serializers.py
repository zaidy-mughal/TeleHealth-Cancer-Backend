from rest_framework import serializers

from api.patients.models import (
    Patient,
    PatientMedicalRecord,
)
from api.patients.choices import (
    Gender,
    IsIodineAllergic,
    CareProviderType,
    TreatmentType,
    AddictionType,
    MaritalStatus,
)
from api.patients.validators import (
    validate_fields,
    validate_existing_record,
    validate_addiction_types,
    validate_care_providers_types,
)
from api.patients.utils.fields import LabelChoiceField
from api.patients.utils.update_handler import (
    update_json_field,
)


class IodineAllergySerializer(serializers.Serializer):
    is_iodine_allergic = LabelChoiceField(choices=IsIodineAllergic.choices)

    def update(self, instance, validated_data):
        try:
            patient = self.context["request"].user.patient
            return update_json_field(patient, "iodine_allergy", validated_data)
        except Exception as e:
            raise serializers.ValidationError(
                {"detail": f"Failed to update iodine allergy: {str(e)}"}
            )


class AllergySerializer(serializers.Serializer):
    name = serializers.CharField(
        max_length=255,
    )


class AllergyListSerializer(serializers.Serializer):
    allergies = AllergySerializer(many=True, allow_empty=True)

    def update(self, instance, validated_data):
        try:
            patient = self.context["request"].user.patient
            return update_json_field(patient, "allergies", validated_data)
        except Exception as e:
            raise serializers.ValidationError(
                {"detail": f"Failed to update allergies: {str(e)}"}
            )


class MedicationSerializer(serializers.Serializer):
    name = serializers.CharField(
        max_length=255,
    )


class MedicationListSerializer(serializers.Serializer):
    medications = MedicationSerializer(many=True, allow_empty=True)

    def update(self, instance, validated_data):
        try:
            patient = self.context["request"].user.patient
            return update_json_field(patient, "medications", validated_data)
        except Exception as e:
            raise serializers.ValidationError(
                {"detail": f"Failed to update medications: {str(e)}"}
            )


class MedicalHistorySerializer(serializers.Serializer):
    name = serializers.CharField(
        max_length=255,
    )


class MedicalHistoryListSerializer(serializers.Serializer):
    medical_histories = MedicalHistorySerializer(many=True, allow_empty=True)

    def update(self, instance, validated_data):
        try:
            patient = self.context["request"].user.patient
            return update_json_field(patient, "medical_histories", validated_data)
        except Exception as e:
            raise serializers.ValidationError(
                {"detail": f"Failed to update Medical Histories: {str(e)}"}
            )


class SurgicalHistorySerializer(serializers.Serializer):
    name = serializers.CharField(
        max_length=255,
    )


class SurgicalHistoryListSerializer(serializers.Serializer):
    surgical_histories = SurgicalHistorySerializer(many=True, allow_empty=True)

    def update(self, instance, validated_data):
        try:
            patient = self.context["request"].user.patient
            return update_json_field(patient, "surgical_histories", validated_data)
        except Exception as e:
            raise serializers.ValidationError(
                {"detail": f"Failed to update Surgical Histories: {str(e)}"}
            )


class CareProviderSerializer(serializers.Serializer):
    name = serializers.CharField(
        max_length=255,
    )
    contact_number = serializers.CharField(
        max_length=15,
    )
    type = LabelChoiceField(choices=CareProviderType.choices)


class CareProviderListSerializer(serializers.Serializer):
    care_providers = CareProviderSerializer(many=True, allow_empty=True)

    def validate(self, data):
        validate_care_providers_types(self, data)
        return super().validate(data)

    def update(self, instance, validated_data):
        try:
            patient = self.context["request"].user.patient
            return update_json_field(patient, "care_providers", validated_data)
        except Exception as e:
            raise serializers.ValidationError(
                {"detail": f"Failed to update Care Providers: {str(e)}"}
            )


class TreatmentReceivedSerializer(serializers.Serializer):
    name = LabelChoiceField(choices=TreatmentType.choices)


class CancerHistorySerializer(serializers.Serializer):
    cancer_type = serializers.CharField(max_length=255)
    year_of_diagnosis = serializers.IntegerField(min_value=1900, max_value=2100)
    treatment_received = TreatmentReceivedSerializer(many=True)


class CancerHistoryListSerializer(serializers.Serializer):
    cancer_history = CancerHistorySerializer(many=True, allow_empty=True)

    def update(self, instance, validated_data):
        try:
            patient = self.context["request"].user.patient
            return update_json_field(patient, "cancer_history", validated_data)
        except Exception as e:
            raise serializers.ValidationError(
                {"detail": f"Failed to update Cancer History: {str(e)}"}
            )


class AddictionHistorySerializer(serializers.ModelSerializer):
    addiction_type = LabelChoiceField(choices=AddictionType.choices)
    total_years = serializers.IntegerField(
        min_value=0,
        help_text="Total years of addiction. Use 0 for no addiction.",
    )


class AddictionHistoryListSerializer(serializers.Serializer):
    addiction_history = AddictionHistorySerializer(
        many=True,
        allow_empty=True,
        required=True,
    )

    def validate(self, data):
        validate_addiction_types(self, data)
        return super().validate(data)

    def update(self, instance, validated_data):
        try:
            patient = self.context["request"].user.patient
            return update_json_field(patient, "addiction_history", validated_data)
        except Exception as e:
            raise serializers.ValidationError(
                {"detail": f"Failed to update addiction history: {str(e)}"}
            )


class PatientMedicalRecordSerializer(serializers.ModelSerializer):
    iodine_allergy = IodineAllergySerializer(read_only=True)
    allergies = AllergyListSerializer(read_only=True)
    medications = MedicationListSerializer(read_only=True)
    medical_histories = MedicalHistoryListSerializer(read_only=True)
    surgical_histories = SurgicalHistoryListSerializer(read_only=True)
    cancer_history = CancerHistoryListSerializer(read_only=True)
    care_providers = CareProviderListSerializer(read_only=True)
    addiction_history = AddictionHistoryListSerializer(read_only=True)

    def create(self, validated_data):
        try:
            patient = self.context["request"].user.patient
            return PatientMedicalRecord.objects.create(
                patient=patient, **validated_data
            )
        except Exception as e:
            raise serializers.ValidationError(
                {"detail": f"Failed to create medical record: {str(e)}"}
            )

    # def create(self, validated_data):
    #     try:
    #         patient = self.context["request"].user.patient

    #         iodine_allergy = validated_data.pop("iodine_allergy", {})
    #         allergies = validated_data.pop("allergies", {})
    #         medications = validated_data.pop("medications", {})
    #         medical_histories = validated_data.pop("medical_histories", {})
    #         surgical_histories = validated_data.pop("surgical_histories", {})
    #         cancer_history = validated_data.pop("cancer_history", {})
    #         care_providers = validated_data.pop("care_providers", {})
    #         addiction_history = validated_data.pop("addiction_history", {})

    #         record = PatientMedicalRecord.objects.create(
    #             patient=patient,
    #             iodine_allergy=iodine_allergy,
    #             allergies=allergies,
    #             medications=medications,
    #             medical_histories=medical_histories,
    #             surgical_histories=surgical_histories,
    #             cancer_history=cancer_history,
    #             care_providers=care_providers,
    #             addiction_history=addiction_history,
    #         )
    #         return record

    #     except Exception as e:
    #         raise serializers.ValidationError(
    #             {"detail": f"Failed to create medical record: {str(e)}"}
    #         )

    class Meta:
        model = PatientMedicalRecord
        fields = [
            "uuid",
            "is_main_record",
            "appointment_uuid",
            "iodine_allergy",
            "allergies",
            "medications",
            "medical_histories",
            "surgical_histories",
            "cancer_history",
            "addiction_history",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "uuid",
            "iodine_allergy",
            "allergies",
            "medications",
            "medical_histories",
            "surgical_histories",
            "cancer_history",
            "addiction_history",
            "created_at",
            "updated_at",
        ]


class PatientSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email")
    first_name = serializers.CharField(source="user.first_name")
    middle_name = serializers.CharField(source="user.middle_name", allow_blank=True)
    last_name = serializers.CharField(source="user.last_name")
    gender = LabelChoiceField(choices=Gender.choices)
    marital_status = LabelChoiceField(choices=MaritalStatus.choices)
    medical_record = serializers.SerializerMethodField()

    def get_medical_record(self, obj):
        try:
            medical_record = obj.medical_records.first()
            return PatientMedicalRecordSerializer(medical_record).data
        except PatientMedicalRecord.DoesNotExist:
            return None

    class Meta:
        model = Patient
        fields = [
            "uuid",
            "email",
            "first_name",
            "middle_name",
            "last_name",
            "date_of_birth",
            "gender",
            "phone_number",
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
        read_only_fields = [
            "uuid",
            "email",
            "first_name",
            "middle_name",
            "last_name",
            "iodine_allergy",
            "allergies",
            "medications",
            "medical_histories",
            "surgical_histories",
            "care_providers",
            "cancer_history",
            "addiction_history",
        ]

    def validate(self, attrs):
        if not self.partial:
            validate_fields(self, attrs)
        return super().validate(attrs)

    def update(self, instance, validated_data):
        try:
            user_data = validated_data.pop("user", None)
            if user_data:
                user = instance.user
                for attr, value in user_data.items():
                    setattr(user, attr, value)
                user.save()

            return super().update(instance, validated_data)
        except Exception as e:
            raise serializers.ValidationError(
                {"detail": f"Failed to update patient: {str(e)}"}
            )
