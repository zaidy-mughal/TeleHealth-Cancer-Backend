from rest_framework import serializers


def validate_fields(self, attrs):
    missing = [
        field
        for field in self.fields
        if field not in attrs and field not in self.Meta.read_only_fields
    ]
    if missing:
        raise serializers.ValidationError(
            {field: "This field is required in the payload." for field in missing}
        )


def validate_addiction_types(self, data):
    """
    Validate that exactly two addiction history records are provided:
    - One for smoking
    - One for alcohol
    """

    addiction_history = data.get("addiction_history", [])

    if len(addiction_history) != 2:
        raise serializers.ValidationError(
            {
                "addiction_history": "Exactly two addiction_type required (one for smoking and one for alcohol)."
            }
        )

    first_record = addiction_history[0].get("addiction_type")
    second_record = addiction_history[1].get("addiction_type")

    if first_record == second_record:
        raise serializers.ValidationError(
            {"addiction_history": "Both records cannot have the same addiction_type."}
        )

    return data


def validate_care_providers_types(self, data):
    """
    Validate that exactly two addiction history records are provided:
    - One for smoking
    - One for alcohol
    """

    care_providers_data = data.get("care_providers", [])

    if len(care_providers_data) != 2:
        raise serializers.ValidationError(
            {
                "care_providers": "Exactly two care_providers required (one for smoking and one for alcohol)."
            }
        )

    first_record = care_providers_data[0].get("type")
    second_record = care_providers_data[1].get("type")

    if first_record == second_record:
        raise serializers.ValidationError(
            {"addiction_history": "Both records cannot have the same care_providers."}
        )

    return data
