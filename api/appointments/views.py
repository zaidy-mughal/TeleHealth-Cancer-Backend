from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from django.core.exceptions import ValidationError
from drf_spectacular.utils import extend_schema

from api.appointments.serializers import AppointmentSerializer
from api.appointments.models import Appointments
from api.patients.models import Patient



@extend_schema(
    tags=["Appointments"],
    request=AppointmentSerializer,
    responses=AppointmentSerializer(many=True),
    description="API for managing appointments.",
)
class AppointmentRetrieveView(RetrieveAPIView):
    """
    API view to handle appointment creation and retrieval.
    Includes validation for appointments and proper error handling.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = AppointmentSerializer

    def get(self, request, *args, **kwargs):
        """
        Retrieve appointments with optional filtering.
        """
        try:
            # filtering appointments by date - not implemented yet - confused
            # date = request.query_params.get("date")

            doctor_id = request.query_params.get("doctor")
            patient_uuid = kwargs.get("patient_uuid")
            if not patient_uuid:
                return Response(
                    {"error": "Patient ID is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            patient_id = Patient.objects.get(uuid=patient_uuid)
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



@extend_schema(
    tags=["Appointments"],
    request=AppointmentSerializer,
    description="API for managing appointments.",
)
class AppointmentCreateView(CreateAPIView):
    """
    API view to handle appointment creation.
    Includes validation for appointments and proper error handling.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = AppointmentSerializer


    def post(self, request):
        """
        Create a new appointment with validation.
        """
        try:
            serializer = self.serializer_class(
                data=request.data,
                context={'request': request}
            )
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

