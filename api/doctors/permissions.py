from rest_framework.permissions import BasePermission
from api.doctors.models import Doctor


class IsDoctor(BasePermission):
    """
    Custom permission to allow only authenticated doctors to access data.

    Global check: User must be authenticated and have a doctor profile.
    Object-level check: only access objects owned by the same patient.
    """

    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and hasattr(user, "doctor")

    def has_object_permission(self, request, view, obj):
        user = request.user

        try:
            doctor = user.doctor
        except Doctor.DoesNotExist:
            return False

        if hasattr(obj, "doctor"):
            return obj.doctor == doctor

        if isinstance(obj, Doctor):
            return obj == doctor

        if hasattr(obj, "user"):
            return obj.user == user

        return False
