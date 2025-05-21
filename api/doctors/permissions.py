from rest_framework.permissions import BasePermission
from api.doctors.models import Doctor


class IsDoctorOrAdmin(BasePermission):
    """
    Custom permission to only allow doctors to access their own data.
    This permission checks:
    1. If the user is authenticated and has a doctor profile
    2. For object-level permissions, checks that the object belongs to the doctor
    """

    def has_permission(self, request, view):
        user = request.user
        # Allow if user is authenticated AND (has a doctor profile OR is admin)
        return user.is_authenticated and (
            hasattr(user, "doctor") or user.is_staff or user.is_superuser
        )

    def has_object_permission(self, request, view, obj):
        user = request.user
        # Allow admins full access
        if user.is_staff or user.is_superuser:
            return True
        try:
            doctor = request.user.doctor
        except Doctor.DoesNotExist:
            return False

        if hasattr(obj, "doctor"):
            return obj.doctor == doctor

        if isinstance(obj, Doctor):
            return obj == doctor

        if hasattr(obj, "user"):
            return obj.user == request.user

        return False
