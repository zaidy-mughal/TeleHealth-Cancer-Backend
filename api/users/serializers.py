from rest_framework.serializers import ModelSerializer
from .models import User

class UserSerializer(ModelSerializer):
    """
    Serializer for the User model.
    This serializer is used to convert User model instances to JSON and vice versa.
    """
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff']
        read_only_fields = ['id', 'is_active', 'is_staff']
        