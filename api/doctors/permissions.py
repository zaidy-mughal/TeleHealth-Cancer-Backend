from rest_framework.permissions import BasePermission

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
        if not request.user.is_authenticated:
            return False
        
        # Check if user has a doctor profile
        if not hasattr(request.user, 'doctor'):
            return False
            
        if hasattr(obj, 'doctor'):
            # For TimeSlot, LicenseInfo and other models with a doctor field
            return obj.doctor == request.user.doctor
        elif hasattr(obj, 'user'):
            # If this is a Doctor object itself
            return obj == request.user.doctor
        
        return False