from rest_framework.permissions import BasePermission

class IsPatient(BasePermission):
    """
    Custom permission to allow only authenticated patients to access data.
    1. User must be authenticated and have a patient profile.
    2. Object-level: only access objects owned by the same patient.
    """

    def has_permission(self, request, view):
        user = request.user
        return user.is_authenticated and hasattr(user, "patient")

    def has_object_permission(self, request, view, obj):
        user = request.user

        if not user.is_authenticated or not hasattr(user, "patient"):
            return False

        if hasattr(obj, "patient"):
            return obj.patient == user.patient
        elif hasattr(obj, "user"):
            return obj.user == user.patient.user

        return False
