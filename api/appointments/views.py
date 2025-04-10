from typing import override
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from django.utils import timezone
from .serializers import AppointmentSerializer
from .models import Appointments


class AppointmentView(APIView):
    """
    API view to handle appointment creation and retrieval.
    Includes validation for appointments and proper error handling.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = AppointmentSerializer

    def validate_request_data(self, data):
        """
        Validate the incoming request data.
        """
        required_fields = ["doctor", "patient", "appointment_date", "appointment_time"]
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            raise ValidationError(
                f"Missing required fields: {', '.join(missing_fields)}"
            )

    def get(self, request, *args, **kwargs):
        """
        Retrieve appointments with optional filtering.
        """
        try:
            # filtering appointments by date - not implemented yet - confused
            # date = request.query_params.get("date")

            doctor_id = request.query_params.get("doctor")
            patient_id = kwargs.get("patient_id")
            if not patient_id:
                return Response(
                    {"error": "Patient ID is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            appointments = Appointments.objects.filter(patient=patient_id)

            if doctor_id:
                appointments = appointments.filter(doctor_id=doctor_id)

            serializer = self.serializer_class(appointments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": f"Failed to retrieve appointments: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request):
        """
        Create a new appointment with validation.
        """
        try:
            self.validate_request_data(request.data)

            serializer = self.serializer_class(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            appointment = serializer.save()

            return Response(
                self.serializer_class(appointment).data, status=status.HTTP_201_CREATED
            )

        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": f"Failed to create appointment: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    
    @override
    def handle_exception(self, exc):
        """
        Handle any unhandled exceptions.
        """
        if isinstance(exc, ValidationError):
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"error": "An unexpected error occurred"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
