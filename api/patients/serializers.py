import logging

from rest_framework import serializers

from api.appointments.models import Appointment
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
from api.patients.utils.get_handler import get_medical_record_data
from api.patients.validators import (
    validate_fields,
    validate_addiction_types,
    validate_care_providers_types,
    validate_only_one_main_record,
)
from api.patients.utils.fields import LabelChoiceField
from api.patients.utils.update_handler import (
    update_json_field,
)

logger = logging.getLogger(__name__)


class IodineAllergySerializer(serializers.Serializer):
    is_iodine_allergic = serializers.ChoiceField(choices=IsIodineAllergic.choices)

    def to_representation(self, instance):
        request = self.context.get("request")
        appointment_uuid = self.context.get("appointment_uuid")
        patient = request.user.patient

        try:
            if appointment_uuid:
                appointment = Appointment.objects.get(uuid=appointment_uuid)
                data = getattr(appointment.medical_record, "iodine_allergy", [])
            else:
                main_record = patient.medical_records.get(is_main_record=True)
                data = getattr(main_record, "iodine_allergy", [])

            return {"iodine_allergy": data}

        except Exception as e:
            logger.exception("Unexpected error")
            raise serializers.ValidationError(
                {"detail": "Failed to get iodine allergy"}
            )

    def update(self, instance, validated_data):
        try:
            return update_json_field(
                self.context, "iodine_allergy", validated_data
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
    allergies = AllergySerializer(many=True, allow_empty=True)

    item_serializer_class = AllergySerializer

    def to_representation(self, instance):
        return get_medical_record_data(
            self.context, "allergies", self.item_serializer_class
        )

    def update(self, instance, validated_data):
        try:
            return update_json_field(
                self.context, "allergies", validated_data
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
    medications = MedicationSerializer(many=True, allow_empty=True)
    item_serializer_class = MedicationSerializer

    def to_representation(self, instance):
        return get_medical_record_data(
            self.context, "medications", self.item_serializer_class
        )

    def update(self, instance, validated_data):
        try:
            return update_json_field(
                self.context, "medications", validated_data
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
    medical_histories = MedicalHistorySerializer(many=True, allow_empty=True)
    item_serializer_class = MedicalHistorySerializer

    def to_representation(self, instance):
        return get_medical_record_data(
            self.context, "medical_histories", self.item_serializer_class
        )

    def update(self, instance, validated_data):
        try:
            return update_json_field(
                self.context, "medical_histories", validated_data
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
    surgical_histories = SurgicalHistorySerializer(many=True, allow_empty=True)
    item_serializer_class = SurgicalHistorySerializer

    def to_representation(self, instance):
        return get_medical_record_data(
            self.context, "surgical_histories", self.item_serializer_class
        )

    def update(self, instance, validated_data):
        try:
            return update_json_field(
                self.context, "surgical_histories", validated_data
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
    type_display = serializers.SerializerMethodField(read_only=True)

    def get_type_display(self, obj):
        return obj.get_type_display()


class CareProviderListSerializer(serializers.Serializer):
    care_providers = CareProviderSerializer(many=True, allow_empty=True)
    item_serializer_class = CareProviderSerializer

    def to_representation(self, instance):
        return get_medical_record_data(
            self.context, "care_providers", self.item_serializer_class
        )

    def validate(self, attrs):
        validate_care_providers_types(self, attrs)
        return super().validate(attrs)

    def update(self, instance, validated_data):
        try:
            return update_json_field(
                self.context, "care_providers", validated_data
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
    cancer_history = CancerHistorySerializer(many=True, allow_empty=True)
    item_serializer_class = CancerHistorySerializer

    def to_representation(self, instance):
        return get_medical_record_data(
            self.context, "cancer_history", self.item_serializer_class
        )

    def update(self, instance, validated_data):
        try:
            return update_json_field(
                self.context, "cancer_history", validated_data
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
    addiction_history = AddictionHistorySerializer(many=True)
    item_serializer_class = AddictionHistorySerializer

    def to_representation(self, instance):
        return get_medical_record_data(
            self.context, "addiction_history", self.item_serializer_class
        )

    def validate(self, attrs):
        validate_addiction_types(self, attrs)
        return super().validate(attrs)

    def update(self, instance, validated_data):
        try:
            return update_json_field(
                self.context, "addiction_history", validated_data
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
    email = serializers.EmailField(source="user.email", read_only=True)
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
