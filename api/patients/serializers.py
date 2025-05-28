from rest_framework import serializers
from cities_light.models import City, Region

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
)
from api.patients.choices import (
    Gender,
    IsIodineAllergic,
    CareProviderType,
    TreatmentType,
    AddictionType,
    VisitType,
    MaritalStatus,
)
from api.patients.validators import (
    validate_fields,
    validate_existing_record,
    validate_addiction_types,
)
from api.patients.utils.fields import LabelChoiceField
from api.patients.utils.relation_handler import (
    PatientRelationHandlerMixin,
    handle_cancer_history_list,
    handle_care_provider,
    handle_addiction_history,
)


class IodineAllergySerializer(serializers.ModelSerializer):
    is_iodine_allergic = LabelChoiceField(choices=IsIodineAllergic.choices)

    class Meta:
        model = IodineAllergy
        fields = ["id", "uuid", "is_iodine_allergic"]
        read_only_fields = ["id", "uuid"]

    def create(self, validated_data):
        try:
            patient = self.context["request"].user.patient

            if IodineAllergy.objects.filter(patient=patient).exists():
                raise serializers.ValidationError(
                    {
                        "detail": "Iodine allergy record already exists. Use PUT/PATCH to update."
                    }
                )

            validated_data["patient"] = patient
            return super().create(validated_data)
        except Exception as e:
            raise serializers.ValidationError(
                {"detail": f"Failed to create iodine allergy record: {str(e)}"}
            )

    def update(self, instance, validated_data):
        try:
            patient = self.context["request"].user.patient
            validated_data["patient"] = patient
            return super().update(instance, validated_data)
        except Exception as e:
            raise serializers.ValidationError(
                {"detail": f"Failed to update iodine allergy record: {str(e)}"}
            )


class AllergySerializer(serializers.ModelSerializer):
    class Meta:
        model = Allergy
        fields = ["id", "uuid", "name"]
        read_only_fields = ["id", "uuid"]


class PatientAllergySerializer(serializers.Serializer, PatientRelationHandlerMixin):
    allergies = AllergySerializer(many=True, allow_empty=True)

    relation_model = PatientAllergy
    target_model = Allergy
    related_field_name = "allergy"
    data_key = "allergies"

    def create(self, validated_data):
        try:
            return self.handle_relation(validated_data, clear_existing=False)
        except Exception as e:
            raise serializers.ValidationError(
                {"detail": f"Failed to create allergies: {str(e)}"}
            )

    def update(self, instance, validated_data):
        try:
            return self.handle_relation(validated_data, clear_existing=True)
        except Exception as e:
            raise serializers.ValidationError(
                {"detail": f"Failed to update allergies: {str(e)}"}
            )

    def to_representation(self, instance):
        allergies = Allergy.objects.filter(allergy_patients__patient=instance)
        return {"allergies": AllergySerializer(allergies, many=True).data}


class MedicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medication
        fields = ["id", "uuid", "name"]
        read_only_fields = ["id", "uuid"]


class PatientMedicationSerializer(serializers.Serializer, PatientRelationHandlerMixin):
    medications = MedicationSerializer(many=True, allow_empty=True)

    relation_model = PatientMedication
    target_model = Medication
    related_field_name = "medication"
    data_key = "medications"

    def create(self, validated_data):
        try:
            return self.handle_relation(validated_data, clear_existing=False)
        except Exception as e:
            raise serializers.ValidationError(
                {"detail": f"Failed to create medications: {str(e)}"}
            )

    def update(self, instance, validated_data):
        try:
            return self.handle_relation(validated_data, clear_existing=True)
        except Exception as e:
            raise serializers.ValidationError(
                {"detail": f"Failed to update medications: {str(e)}"}
            )

    def to_representation(self, instance):
        medications = Medication.objects.filter(medication_patients__patient=instance)
        return {"medications": MedicationSerializer(medications, many=True).data}


class MedicalHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalHistory
        fields = ["id", "uuid", "name"]


class PatientMedicalHistorySerializer(
    serializers.Serializer, PatientRelationHandlerMixin
):
    medical_histories = MedicalHistorySerializer(many=True, allow_empty=True)

    relation_model = PatientMedicalHistory
    target_model = MedicalHistory
    related_field_name = "medical_history"
    data_key = "medical_histories"

    def create(self, validated_data):
        try:
            return self.handle_relation(validated_data, clear_existing=False)
        except Exception as e:
            raise serializers.ValidationError(
                {"detail": f"Failed to create medical histories: {str(e)}"}
            )

    def update(self, instance, validated_data):
        try:
            return self.handle_relation(validated_data, clear_existing=True)
        except Exception as e:
            raise serializers.ValidationError(
                {"detail": f"Failed to update medical histories: {str(e)}"}
            )

    def to_representation(self, instance):
        medical_histories = MedicalHistory.objects.filter(
            medical_history_patients__patient=instance
        )
        return {
            "medical_histories": MedicalHistorySerializer(
                medical_histories, many=True
            ).data
        }


class SurgicalHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SurgicalHistory
        fields = ["id", "uuid", "name"]


class PatientSurgicalHistorySerializer(
    serializers.Serializer, PatientRelationHandlerMixin
):
    surgical_histories = SurgicalHistorySerializer(many=True, allow_empty=True)

    relation_model = PatientSurgicalHistory
    target_model = SurgicalHistory
    related_field_name = "surgical_history"
    data_key = "surgical_histories"

    def create(self, validated_data):
        try:
            return self.handle_relation(validated_data, clear_existing=False)
        except Exception as e:
            raise serializers.ValidationError(
                {"detail": f"Failed to create surgical histories: {str(e)}"}
            )

    def update(self, instance, validated_data):
        try:
            return self.handle_relation(validated_data, clear_existing=True)
        except Exception as e:
            raise serializers.ValidationError(
                {"detail": f"Failed to update surgical histories: {str(e)}"}
            )

    def to_representation(self, instance):
        surgical_histories = SurgicalHistory.objects.filter(
            surgical_history_patients__patient=instance
        )
        return {
            "surgical_histories": MedicalHistorySerializer(
                surgical_histories, many=True
            ).data
        }


class CareProviderSerializer(serializers.ModelSerializer):
    type = LabelChoiceField(choices=CareProviderType.choices)

    class Meta:
        model = CareProvider
        fields = ["id", "uuid", "name", "contact_number", "type"]


class PatientCareProviderSerializer(serializers.Serializer):
    care_providers = CareProviderSerializer(many=True, allow_empty=True)

    def create(self, validated_data):
        try:
            patient = self.context["request"].user.patient
            validated_data["patient"] = patient
            return handle_care_provider(validated_data, clear_existing=False)
        except Exception as e:
            raise serializers.ValidationError(
                {"detail": f"Failed to create care providers: {str(e)}"}
            )

    def update(self, instance, validated_data):
        try:
            patient = self.context["request"].user.patient
            validated_data["patient"] = patient
            return handle_care_provider(validated_data, clear_existing=True)
        except Exception as e:
            raise serializers.ValidationError(
                {"detail": f"Failed to update care providers: {str(e)}"}
            )

    def to_representation(self, instance):
        care_providers = SurgicalHistory.objects.filter(
            care_provider_patients__patient=instance
        )
        return {
            "care_providers": MedicalHistorySerializer(care_providers, many=True).data
        }


class CancerTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CancerType
        fields = ["id", "uuid", "name"]


class TreatmentReceivedSerializer(serializers.ModelSerializer):
    name = LabelChoiceField(choices=TreatmentType.choices)

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


class CancerHistoryListSerializer(serializers.Serializer):
    cancer_histories = CancerHistorySerializer(many=True, allow_empty=True)

    def create(self, validated_data):
        try:
            patient = self.context["request"].user.patient
            validated_data["patient"] = patient
            return handle_cancer_history_list(validated_data, clear_existing=False)
        except Exception as e:
            raise serializers.ValidationError(
                {"detail": f"Failed to create cancer history: {str(e)}"}
            )

    def update(self, instance, validated_data):
        try:
            patient = self.context["request"].user.patient
            validated_data["patient"] = patient
            return handle_cancer_history_list(validated_data, clear_existing=True)
        except Exception as e:
            raise serializers.ValidationError(
                {"detail": f"Failed to update cancer history: {str(e)}"}
            )


class AddictionHistorySerializer(serializers.ModelSerializer):
    addiction_type = LabelChoiceField(choices=AddictionType.choices)

    class Meta:
        model = AddictionHistory
        fields = ["id", "uuid", "addiction_type", "total_years"]


class PatientAddictionHistorySerializer(serializers.Serializer):
    addiction_history = AddictionHistorySerializer(
        many=True, allow_empty=True, required=True
    )

    def validate(self, data):
        validate_addiction_types(self, data)
        return super().validate(data)

    def create(self, validated_data):
        try:
            validate_existing_record(self, AddictionHistory)
            patient = self.context["request"].user.patient
            validated_data["patient"] = patient
            return handle_addiction_history(validated_data, clear_existing=False)
        except Exception as e:
            raise serializers.ValidationError(
                {"detail": f"Failed to create addiction history: {str(e)}"}
            )
        
    def update(self, instance, validated_data):
        try:
            patient = self.context["request"].user.patient
            validated_data["patient"] = patient
            return handle_addiction_history(validated_data, clear_existing=True)
        except Exception as e:
            raise serializers.ValidationError(
                {"detail": f"Failed to update addiction history: {str(e)}"}
            )


class PatientSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email")
    first_name = serializers.CharField(source="user.first_name")
    middle_name = serializers.CharField(source="user.middle_name")
    last_name = serializers.CharField(source="user.last_name")
    gender = LabelChoiceField(choices=Gender.choices)
    visit_type = LabelChoiceField(choices=VisitType.choices)
    marital_status = LabelChoiceField(choices=MaritalStatus.choices)
    
    city = serializers.SlugRelatedField(slug_field='name', queryset=City.objects.all())
    state = serializers.SlugRelatedField(slug_field='name', queryset=Region.objects.all())

    iodine_allergy = IodineAllergySerializer(read_only=True)
    cancer_history = CancerHistorySerializer(
        many=True, allow_empty=True, read_only=True
    )
    addiction_history = AddictionHistorySerializer(
        many=True, allow_empty=True, read_only=True
    )

    surgical_histories = serializers.SerializerMethodField(read_only=True)
    allergies = serializers.SerializerMethodField(read_only=True)
    medications = serializers.SerializerMethodField(read_only=True)
    medical_histories = serializers.SerializerMethodField(read_only=True)
    care_providers = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Patient
        fields = [
            "id",
            "uuid",
            "email",
            "first_name",
            "middle_name",
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
        read_only_fields = [
            "id",
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

    def get_allergies(self, obj):
        patient_allergies = obj.allergies.all()
        allergy_objects = [pa.allergy for pa in patient_allergies]
        return AllergySerializer(allergy_objects, many=True).data

    def get_surgical_histories(self, obj):
        patient_surgical_histories = obj.surgical_histories.all()
        surgical_history_objects = [
            psh.surgical_history for psh in patient_surgical_histories
        ]
        return SurgicalHistorySerializer(surgical_history_objects, many=True).data

    def get_medical_histories(self, obj):
        patient_medical_histories = obj.medical_histories.all()
        medical_history_objects = [
            pmh.medical_history for pmh in patient_medical_histories
        ]
        return MedicalHistorySerializer(medical_history_objects, many=True).data

    def get_medications(self, obj):
        patient_medications = obj.medications.all()
        medication_objects = [pm.medication for pm in patient_medications]
        return MedicationSerializer(medication_objects, many=True).data

    def get_care_providers(self, obj):
        patient_care_providers = obj.care_providers.all()
        care_provider_objects = [pcp.care_provider for pcp in patient_care_providers]
        return CareProviderSerializer(care_provider_objects, many=True).data
