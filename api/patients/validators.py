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
        raise serializers.ValidationError({
            "detail": f"{model_name} record already exists. Use PUT to update."
        })