from rest_framework.permissions import BasePermission

class IsPatient(BasePermission):
    """
    Custom permission to only allow patients to access their own data.
    This permission checks:
    1. If the user is authenticated and has a patient profile
    2. For object-level permissions, checks that the object belongs to the patient
    """
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'patient')
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        if not hasattr(request.user, 'patient'):
            return False
            
        if hasattr(obj, 'patient'):
            return obj.patient == request.user.patient
        elif hasattr(obj, 'user'):
            return obj == request.user.patient
        
        return False