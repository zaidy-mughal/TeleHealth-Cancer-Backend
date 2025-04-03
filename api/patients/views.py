from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Patient
from .serializers import PatientSerializer, PatientRegistrationSerializer


class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [permissions.AllowAny]  # Allow any user to access the API

    def get_serializer_class(self):
        if self.action == "register":
            return PatientRegistrationSerializer
        return PatientSerializer

    @action(detail=False, methods=["post"], permission_classes=[permissions.AllowAny])
    def register(self, request):
        """Register a new patient"""
        # dynamically set the serializer class
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                patient = serializer.save()
                return Response(
                    PatientSerializer(patient).data, status=status.HTTP_201_CREATED
                )
            except Exception as e:
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["get"])
    def me(self, request):
        """
        Get the current user's profile.

        This requires authentication in a real application.
        """
        if request.user.is_authenticated:
            try:
                patient = request.user.patient_profile
                serializer = self.get_serializer(patient)
                return Response(serializer.data)
            except Patient.DoesNotExist:
                return Response(
                    {"detail": "Patient profile not found for this user."},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            return Response(
                {"detail": "Authentication required."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    @action(detail=False, methods=["get"], permission_classes=[permissions.AllowAny])
    def demo(self, request):
        """
        For demo/testing purposes - get the most recent patient.
        """
        patient = Patient.objects.order_by("-created_at").first()

        if not patient:
            return Response(
                {"detail": "No patient profiles found. Please create a patient first."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = self.get_serializer(patient)
        return Response(serializer.data)

    @action(detail=True, methods=["patch"])
    def update_cancer_info(self, request, pk=None):
        """
        Update cancer-related information for a patient
        """
        patient = self.get_object()

        # Only allow updates to these specific fields
        allowed_fields = ["cancer_type", "cancer_duration", "visit_type"]
        update_data = {k: v for k, v in request.data.items() if k in allowed_fields}

        serializer = self.get_serializer(patient, data=update_data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
