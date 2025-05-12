from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from api.doctors.serializers import (
    SpecializationSerializer,
    DoctorSerializer,
    TimeSlotSerializer,
    LicenseInfoSerializer,
)
from api.doctors.filters import DoctorFilter
from api.doctors.permissions import IsDoctor
from api.doctors.models import Specialization, TimeSlot, LicenseInfo, Doctor
from drf_spectacular.utils import extend_schema

import logging
logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name="dispatch")
class SpecializationListCreateView(ListCreateAPIView):
    """
    API view to handle specialization creation and listing.
    """

    permission_classes = [IsAuthenticated, IsDoctor]
    serializer_class = SpecializationSerializer
    queryset = Specialization.objects.all()
    


@method_decorator(csrf_exempt, name="dispatch")
class DoctorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = DoctorFilter


@method_decorator(csrf_exempt, name="dispatch")
class TimeSlotListAPIView(APIView):
    """
    API view to handle time slot listing.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = TimeSlotSerializer

    def get(self, request, *args, **kwargs):
        try:
            doctor_uuid = kwargs.get("doctor_uuid")
            doctor = Doctor.objects.get(uuid=doctor_uuid)

            time_slots = TimeSlot.objects.filter(doctor=doctor, is_booked=False)
            serializer = self.serializer_class(time_slots, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except TimeSlot.DoesNotExist:
            return Response(
                {"error": "Time slots not found."}, status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            logger.error(f"Error retrieving time slots: {str(e)}")
            return Response(
                {"error": f"Failed to retrieve time slots: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@method_decorator(csrf_exempt, name="dispatch")
class TimeSlotCreateAPIView(APIView):
    """
    Handles bulk creation of time slots using Django's bulk_create.
    Expects a list of time slot data and minimum one object in list.
    """

    serializer_class = TimeSlotSerializer
    permission_classes = [IsAuthenticated, IsDoctor]

    def post(self, request, *args, **kwargs):
        data = request.data

        if not isinstance(data, list):
            return Response(
                {"detail": "Expected a list of time slots."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not data:
            return Response(
                {"detail": "At least one time slot must be provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            time_slot_objects = self._build_time_slot_objects(data, request)

            created_slots = TimeSlot.objects.bulk_create(
                time_slot_objects, batch_size=15
            )

            response_serializer = self.serializer_class(created_slots, many=True)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        except serializers.ValidationError as e:
            return Response({"detail": e.detail}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error creating time slots: {str(e)}")
            return Response(
                {"error": f"Failed to create time slots: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @transaction.atomic
    def _build_time_slot_objects(self, data, request):
        """
        Validates input data and builds TimeSlot instances.
        """
        time_slot_objects = []

        for item in data:
            serializer = self.serializer_class(data=item, context={"request": request})
            serializer.is_valid(raise_exception=True)

            validated_data = serializer.validated_data
            time_slot = TimeSlot(
                doctor=request.user.doctor,
                start_time=validated_data["start_time"],
                end_time=validated_data["end_time"],
            )
            time_slot_objects.append(time_slot)

        return time_slot_objects


@method_decorator(csrf_exempt, name="dispatch")
class LicenseInfoListAPIView(APIView):
    """
    API view to handle license information listing.
    """

    permission_classes = [IsAuthenticated, IsDoctor]
    serializer_class = LicenseInfoSerializer

    def get(self, request, *args, **kwargs):
        try:
            doctor = request.user.doctor
            license_info = LicenseInfo.objects.filter(doctor=doctor)
            serializer = self.serializer_class(license_info, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except LicenseInfo.DoesNotExist:
            return Response(
                {"error": "License information not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        except Exception as e:
            logger.error(f"Error retrieving license information: {str(e)}")
            return Response(
                {"error": f"Failed to retrieve license information: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


@method_decorator(csrf_exempt, name="dispatch")
class LicenseInfoCreateAPIView(APIView):
    """
    API view to handle license information creation.
    """

    permission_classes = [IsAuthenticated, IsDoctor]
    serializer_class = LicenseInfoSerializer

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.serializer_class(
                data=request.data, context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except serializers.ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error creating license information: {str(e)}")
            return Response(
                {"error": f"Failed to create License Info: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
