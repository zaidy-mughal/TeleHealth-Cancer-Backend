from django.db.models import Prefetch
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError as DRFValidationError


from api.doctors.serializers import (
    SpecializationSerializer,
    DoctorSerializer,
    TimeSlotDeleteSerializer,
    TimeSlotSerializer,
    TimeSlotCreateSerializer,
    LicenseInfoSerializer,
    BulkTimeSlotCreateSerializer,
    BulkTimeSlotDeleteSerializer,
)
from api.doctors.filters import DoctorFilter, TimeSlotFilter
from api.doctors.permissions import IsDoctorOrAdmin
from api.patients.permissions import IsPatientOrAdmin
from api.doctors.models import Specialization, TimeSlot, LicenseInfo, Doctor
from api.utils.exception_handler import HandleExceptionAPIView, HandleExceptionViewset

import logging

logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name="dispatch")
class SpecializationListCreateView(HandleExceptionAPIView, ListCreateAPIView):
    """
    API view to handle specialization creation and listing.
    """

    permission_classes = [IsAuthenticated, IsDoctorOrAdmin]
    serializer_class = SpecializationSerializer
    queryset = Specialization.objects.all()


@method_decorator(csrf_exempt, name="dispatch")
class DoctorViewSet(HandleExceptionViewset, viewsets.ReadOnlyModelViewSet):
    serializer_class = DoctorSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = DoctorFilter
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        available_slots = TimeSlot.objects.filter(
            is_booked=False, start_time__gte=timezone.now()
        )

        return (
            Doctor.objects.filter(time_slots__in=available_slots)
            .distinct()
            .prefetch_related(Prefetch("time_slots", queryset=available_slots))
        )

    def filter_queryset(self, queryset):
        try:
            return super().filter_queryset(queryset)
        except DjangoValidationError as e:
            detail = e.message_dict if hasattr(e, "message_dict") else str(e)
            raise DRFValidationError(detail=detail)


@method_decorator(csrf_exempt, name="dispatch")
class AvailableDoctorDatesAPIView(HandleExceptionAPIView, APIView):
    permission_classes = [IsPatientOrAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_class = TimeSlotFilter

    def get(self, request, *args, **kwargs):

        base_filter = {"is_booked": False, "start_time__gte": timezone.now()}
        queryset = TimeSlot.objects.filter(**base_filter)

        filterset = self.filterset_class(request.query_params, queryset=queryset)

        if not filterset.is_valid():
            return Response(
                {"error": "Invalid filter parameters", "details": filterset.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # get queryset from filterset
        filtered_queryset = filterset.qs
        available_slot_dates = (
            filtered_queryset.values_list("start_time__date", flat=True)
            .distinct()
            .order_by("start_time__date")
        )

        return Response(
            {
                "available_dates": list(available_slot_dates),
            },
            status=status.HTTP_200_OK,
        )


@method_decorator(csrf_exempt, name="dispatch")
class TimeSlotListAPIView(HandleExceptionAPIView, APIView):
    """
    API view to handle time slot listing.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = TimeSlotSerializer

    def get(self, request, *args, **kwargs):
        doctor_uuid = kwargs.get("doctor_uuid")
        doctor = Doctor.objects.get(uuid=doctor_uuid)

        time_slots = TimeSlot.objects.filter(doctor=doctor)
        serializer = self.serializer_class(time_slots, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name="dispatch")
class TimeSlotCreateAPIView(HandleExceptionAPIView, APIView):
    """
    Handles bulk creation of time slots using Django's bulk_create.
    This View is used to create timeslots weekly
    """

    serializer_class = TimeSlotCreateSerializer
    permission_classes = [IsAuthenticated, IsDoctorOrAdmin]

    def post(self, request, *args, **kwargs):
        data = request.data

        serializer = self.serializer_class(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


@method_decorator(csrf_exempt, name="dispatch")
class TimeSlotDeleteAPIView(HandleExceptionAPIView, APIView):
    """
    API View to delete timeslots weekly.
    """

    permission_classes = [IsAuthenticated, IsDoctorOrAdmin]
    serializer_class = TimeSlotDeleteSerializer

    def delete(self, request):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )

        serializer.is_valid(raise_exception=True)
        deleted_count = serializer.delete_timeslots()
        return Response(
            {
                "message": f"Successfully deleted {deleted_count} timeslots",
                "deleted_count": deleted_count,
            },
            status=status.HTTP_200_OK,
        )


class BulkTimeSlotDeleteAPIView(HandleExceptionAPIView, APIView):
    """
    API view to handle bulk deletion of time slots.
    """

    permission_classes = [IsAuthenticated, IsDoctorOrAdmin]
    serializer_class = BulkTimeSlotDeleteSerializer

    def delete(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        response_data = serializer.delete_timeslots()

        return Response(
            response_data,
            status=status.HTTP_200_OK,
        )


@method_decorator(csrf_exempt, name="dispatch")
class LicenseInfoListAPIView(HandleExceptionAPIView, APIView):
    """
    API view to handle license information listing.
    """

    permission_classes = [IsAuthenticated, IsDoctorOrAdmin]
    serializer_class = LicenseInfoSerializer

    def get(self, request, *args, **kwargs):

        doctor = request.user.doctor
        license_info = LicenseInfo.objects.filter(doctor=doctor)
        serializer = self.serializer_class(license_info, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


@method_decorator(csrf_exempt, name="dispatch")
class LicenseInfoCreateAPIView(HandleExceptionAPIView, APIView):
    """
    API view to handle license information creation.
    """

    permission_classes = [IsAuthenticated, IsDoctorOrAdmin]
    serializer_class = LicenseInfoSerializer

    def post(self, request, *args, **kwargs):

        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@method_decorator(csrf_exempt, name="dispatch")
class BulkTimeSlotCreateAPIView(HandleExceptionAPIView, APIView):
    """
    API view to handle bulk time slot creation for multiple months.
    """

    permission_classes = [IsDoctorOrAdmin]
    serializer_class = BulkTimeSlotCreateSerializer

    def post(self, request, *args, **kwargs):

        serializer = BulkTimeSlotCreateSerializer(
            data=request.data, context={"request": request}
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        created_slots = serializer.create_time_slots()

        return Response(
            {
                "message": f"Successfully created {len(created_slots)} time slots",
                "created_count": len(created_slots),
                "months_generated": serializer.validated_data["no_of_months"],
            },
            status=status.HTTP_201_CREATED,
        )
