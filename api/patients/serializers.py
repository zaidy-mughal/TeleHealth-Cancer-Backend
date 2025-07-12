import logging

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
    validate_addiction_types,
    validate_care_providers_types,
    validate_is_appointment_update,
    validate_only_one_main_record,
)
from api.patients.utils.fields import LabelChoiceField
from api.patients.utils.update_handler import (
    update_json_field,
)

logger = logging.getLogger(__name__)


class IodineAllergySerializer(serializers.Serializer):
    appointment_uuid = serializers.UUIDField(required=False, write_only=True)
    is_iodine_allergic = serializers.ChoiceField(choices=IsIodineAllergic.choices)

    def validate(self, attrs):
        validate_is_appointment_update(self, attrs)
        return super().validate(attrs)

    def update(self, instance, validated_data):
        try:
            patient = self.context["request"].user.patient
            is_appointment_update = self.context.get("is_appointment_update", False)
            return update_json_field(
                patient, "iodine_allergy", validated_data, is_appointment_update
            )
        except Exception as e:
            logger.exception("Unexpected error")
            raise serializers.ValidationError(
                {"detail": "Failed to update iodine allergy"}
            )


class AllergySerializer(serializers.Serializer):
    name = serializers.CharField(
        max_length=255,
    )


class AllergyListSerializer(serializers.Serializer):
    appointment_uuid = serializers.UUIDField(required=False, write_only=True)
    allergies = AllergySerializer(many=True, allow_empty=True)

    def validate(self, attrs):
        validate_is_appointment_update(self, attrs)
        return super().validate(attrs)

    def update(self, instance, validated_data):
        try:
            patient = self.context["request"].user.patient
            is_appointment_update = self.context.get("is_appointment_update", False)
            return update_json_field(
                patient, "allergies", validated_data, is_appointment_update
            )
        except Exception as e:
            logger.exception("Unexpected error")
            raise serializers.ValidationError(
                {"detail": "Failed to update allergies"}
            )


class MedicationSerializer(serializers.Serializer):
    name = serializers.CharField(
        max_length=255,
    )


class MedicationListSerializer(serializers.Serializer):
    appointment_uuid = serializers.UUIDField(required=False, write_only=True)
    medications = MedicationSerializer(many=True, allow_empty=True)

    def validate(self, attrs):
        validate_is_appointment_update(self, attrs)
        return super().validate(attrs)

    def update(self, instance, validated_data):
        try:
            patient = self.context["request"].user.patient
            is_appointment_update = self.context.get("is_appointment_update", False)
            return update_json_field(
                patient, "medications", validated_data, is_appointment_update
            )
        except Exception as e:
            logger.exception("Unexpected error")
            raise serializers.ValidationError(
                {"detail": "Failed to update medications"}
            )


class MedicalHistorySerializer(serializers.Serializer):
    name = serializers.CharField(
        max_length=255,
    )


class MedicalHistoryListSerializer(serializers.Serializer):
    appointment_uuid = serializers.UUIDField(required=False, write_only=True)
    medical_histories = MedicalHistorySerializer(many=True, allow_empty=True)

    def validate(self, attrs):
        validate_is_appointment_update(self, attrs)
        return super().validate(attrs)

    def update(self, instance, validated_data):
        try:
            patient = self.context["request"].user.patient
            is_appointment_update = self.context.get("is_appointment_update", False)
            return update_json_field(
                patient, "medical_histories", validated_data, is_appointment_update
            )
        except Exception as e:
            logger.exception("Unexpected error")
            raise serializers.ValidationError(
                {"detail": "Failed to update Medical Histories"}
            )


class SurgicalHistorySerializer(serializers.Serializer):
    name = serializers.CharField(
        max_length=255,
    )


class SurgicalHistoryListSerializer(serializers.Serializer):
    appointment_uuid = serializers.UUIDField(required=False, write_only=True)
    surgical_histories = SurgicalHistorySerializer(many=True, allow_empty=True)

    def validate(self, attrs):
        validate_is_appointment_update(self, attrs)
        return super().validate(attrs)

    def update(self, instance, validated_data):
        try:
            patient = self.context["request"].user.patient
            is_appointment_update = self.context.get("is_appointment_update", False)
            return update_json_field(
                patient, "surgical_histories", validated_data, is_appointment_update
            )
        except Exception as e:
            logger.exception("Unexpected error")
            raise serializers.ValidationError(
                {"detail": "Failed to update Surgical Histories"}
            )


class CareProviderSerializer(serializers.Serializer):
    name = serializers.CharField(
        max_length=255,
    )
    contact_number = serializers.CharField(
        max_length=15,
    )
    type = serializers.ChoiceField(choices=CareProviderType.choices)


class CareProviderListSerializer(serializers.Serializer):
    appointment_uuid = serializers.UUIDField(required=False, write_only=True)
    care_providers = CareProviderSerializer(many=True, allow_empty=True)

    def validate(self, attrs):
        validate_is_appointment_update(self, attrs)
        validate_care_providers_types(self, attrs)
        return super().validate(attrs)

    def update(self, instance, validated_data):
        try:
            patient = self.context["request"].user.patient
            is_appointment_update = self.context.get("is_appointment_update", False)
            return update_json_field(
                patient, "care_providers", validated_data, is_appointment_update
            )
        except Exception as e:
            logger.exception("Unexpected error")
            raise serializers.ValidationError(
                {"detail": "Failed to update Care Providers"}
            )


class TreatmentReceivedSerializer(serializers.Serializer):
    name = serializers.ChoiceField(choices=TreatmentType.choices)


class CancerHistorySerializer(serializers.Serializer):
    cancer_type = serializers.CharField(max_length=255)
    year_of_diagnosis = serializers.IntegerField(min_value=1900, max_value=2100)
    treatment_received = TreatmentReceivedSerializer(many=True)


class CancerHistoryListSerializer(serializers.Serializer):
    appointment_uuid = serializers.UUIDField(required=False, write_only=True)
    cancer_history = CancerHistorySerializer(many=True, allow_empty=True)

    def validate(self, attrs):
        validate_is_appointment_update(self, attrs)
        return super().validate(attrs)

    def update(self, instance, validated_data):
        try:
            patient = self.context["request"].user.patient
            is_appointment_update = self.context.get("is_appointment_update", False)
            return update_json_field(
                patient, "cancer_history", validated_data, is_appointment_update
            )
        except Exception as e:
            logger.exception("Unexpected error")
            raise serializers.ValidationError(
                {"detail": f"Failed to update Cancer History"}
            )


class AddictionHistorySerializer(serializers.Serializer):
    addiction_type = serializers.ChoiceField(choices=AddictionType.choices)
    total_years = serializers.IntegerField(
        min_value=0,
        help_text="Total years of addiction. Use 0 for no addiction.",
    )


class AddictionHistoryListSerializer(serializers.Serializer):
    appointment_uuid = serializers.UUIDField(required=False, write_only=True)
    addiction_history = AddictionHistorySerializer(
        many=True,
        required=True,
    )

    def validate(self, attrs):
        validate_is_appointment_update(self, attrs)
        validate_addiction_types(self, attrs)
        return super().validate(attrs)

    def update(self, instance, validated_data):
        try:
            patient = self.context["request"].user.patient
            is_appointment_update = self.context.get("is_appointment_update", False)
            return update_json_field(
                patient, "addiction_history", validated_data, is_appointment_update
            )
        except Exception as e:
            logger.exception("Unexpected error")
            raise serializers.ValidationError(
                {"detail": "Failed to update addiction history"}
            )


class PatientMedicalRecordSerializer(serializers.ModelSerializer):

    def validate(self, attrs):
        validate_only_one_main_record(self, attrs)
        return super().validate(attrs)

    def create(self, validated_data):
        try:
            patient = self.context["request"].user.patient
            return PatientMedicalRecord.objects.create(
                patient=patient, **validated_data
            )
        except Exception as e:
            logger.exception("Unexpected error")
            raise serializers.ValidationError(
                {"detail": "Failed to create medical record"}
            )

    class Meta:
        model = PatientMedicalRecord
        fields = [
            "uuid",
            "is_main_record",
            "iodine_allergy",
            "allergies",
            "medications",
            "medical_histories",
            "surgical_histories",
            "cancer_history",
            "addiction_history",
            "care_providers",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "uuid",
            "is_main_record",
            "iodine_allergy",
            "allergies",
            "medications",
            "medical_histories",
            "surgical_histories",
            "care_providers",
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
            medical_record = obj.medical_records.get(is_main_record=True)
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
            "medical_record",
        ]
        read_only_fields = [
            "uuid",
            "email",
            "first_name",
            "middle_name",
            "last_name",
            "medical_record",
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
            logger.exception("Unexpected error")
            raise serializers.ValidationError(
                {"detail": "Failed to update patient"}
            )
