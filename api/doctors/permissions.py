from rest_framework.permissions import BasePermission
from api.doctors.models import Doctor

class IsDoctor(BasePermission):
    """
    Custom permission to only allow doctors to access their own data.
    This permission checks:
    1. If the user is authenticated and has a doctor profile
    2. For object-level permissions, checks that the object belongs to the doctor
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'doctor')
    
    def has_object_permission(self, request, view, obj):
        try:
            doctor = request.user.doctor
        except Doctor.DoesNotExist:
            return False

        if hasattr(obj, 'doctor'):
            return obj.doctor == doctor

        if isinstance(obj, Doctor):
            return obj == doctor

        if hasattr(obj, 'user'):
            return obj.user == request.user

        return False