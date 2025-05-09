from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend

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


class SpecializationListCreateView(ListCreateAPIView):
    """
    API view to handle specialization creation and listing.
    """

    permission_classes = [IsAuthenticated, IsDoctor]
    serializer_class = SpecializationSerializer
    queryset = Specialization.objects.all()




class DoctorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    lookup_field = "uuid" # Use UUID as the lookup field
    filter_backends = [DjangoFilterBackend]
    filterset_class = DoctorFilter


class TimeSlotListAPIView(APIView):
    """
    API view to handle time slot listing.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = TimeSlotSerializer

    def get(self, request, *args, **kwargs):
        try:
            doctor_uuid = kwargs.get("doctor_uuid")

            time_slots = TimeSlot.objects.filter(doctor=doctor_uuid)
            serializer = self.serializer_class(time_slots, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except TimeSlot.DoesNotExist:
            return Response(
                {"error": "Time slots not found."}, status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            return Response(
                {"error": f"Failed to retrieve time slots: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )



class TimeSlotCreateAPIView(APIView):
    """
    It Handles bulk creation of time slots using Django's bulk_create.
    It Expects a list of time slot data.
    """
    serializer_class = TimeSlotSerializer
    permission_classes = [IsAuthenticated, IsDoctor]

    def post(self, request, *args, **kwargs):
        if not isinstance(request.data, list):
            return Response(
                {"detail": "Expected a list of time slots."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(request.data) == 0:
            return Response(
                {"detail": "At least one time slot must be provided."},
                status=status.HTTP_400_BAD_REQUEST
            )

        time_slot_objects = []
        
        with transaction.atomic():
            for item in request.data:
                item['doctor'] = request.user.doctor.id
                
                serializer = self.get_serializer(data=item)
                serializer.is_valid(raise_exception=True)
                
                # Instead of saving each serializer, making objects for bulk_create
                validated_data = serializer.validated_data
                time_slot = TimeSlot(
                    doctor=validated_data['doctor'],
                    start_time=validated_data['start_time'],
                    end_time=validated_data['end_time'],
                )
                time_slot_objects.append(time_slot)
            
            # Use bulk_create to insert all objects in a single query
            created_time_slots = TimeSlot.objects.bulk_create(time_slot_objects, batch_size=15)
        
        response_serializer = self.get_serializer(created_time_slots, many=True)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)



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
            return Response(
                {"error": f"Failed to retrieve license information: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


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
            return Response(
                {"error": f"Failed to create License Info: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
