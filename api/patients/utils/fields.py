from rest_framework import serializers


class LabelChoiceField(serializers.ChoiceField):
    """
    DRF field that accepts labels as input and returns labels as output,
    while storing the actual database value (integer or text).
    """

    def to_representation(self, value):
        return self._choices.get(value, value)

    def to_internal_value(self, data):
        data = str(data).lower()
        lowercase_choices = [str(val).lower() for val in self._choices.values()]

        if data in lowercase_choices:
            # Convert label to value
            for key, val in self._choices.items():
                if str(data).lower() == str(val).lower():
                    return key
        self.fail("invalid_choice", input=data)
