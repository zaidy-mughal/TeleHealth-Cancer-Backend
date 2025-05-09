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