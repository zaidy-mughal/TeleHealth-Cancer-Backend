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


def validate_existing_record(serializer, model_class):
    """
    Validate if a patient record already exists.
    """
    if serializer.instance:
        return

    request = serializer.context.get("request")
    if not request or not hasattr(request, "user"):
        return

    patient = request.user.patient
    if model_class.objects.filter(patient=patient).exists():
        model_name = model_class.__name__
        raise serializers.ValidationError(
            {"detail": f"{model_name} record already exists. Use PUT to update."}
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
