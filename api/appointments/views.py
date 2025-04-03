from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Appointment, Doctor, DoctorAvailability, AvailabilityException
from .serializers import (
    AppointmentSerializer, DoctorSerializer,
    DoctorAvailabilitySerializer, AvailabilityExceptionSerializer,
    AppointmentBookingSerializer
)
from api.patients.models import Patient

class DoctorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [permissions.AllowAny]  # Allow anyone to see doctors

    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        """Get doctor's availability for a given date range"""
        doctor = self.get_object()
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not start_date or not end_date:
            return Response(
                {"detail": "start_date and end_date query parameters are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # To be implemented:
        # Implement logic to calculate available slots for the doctor
        available_slots = []  # Replace with actual logic

        return Response(available_slots)


class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [permissions.AllowAny]  # Allow any access

    @action(detail=False, methods=['post'])
    def book(self, request):
        """Book a new appointment"""
        serializer = AppointmentBookingSerializer(data=request.data)

        if serializer.is_valid():
            patient_id = request.data.get('patient_id')
            try:
                patient = Patient.objects.get(id=patient_id)
            except Patient.DoesNotExist:
                return Response(
                    {"detail": "Patient not found"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                doctor = Doctor.objects.get(id=serializer.validated_data['doctor_id'])
            except Doctor.DoesNotExist:
                return Response(
                    {"detail": "Doctor not found"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Combine date and time to get appointment datetime
            appointment_datetime = timezone.make_aware(
                timezone.datetime.combine(
                    serializer.validated_data['date'],
                    serializer.validated_data['time']
                )
            )
            if appointment_datetime <= timezone.now():
                return Response(
                    {"detail": "Cannot schedule appointments in the past"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Create appointment
            appointment = Appointment.objects.create(
                patient=patient,
                doctor=doctor,
                doctor_name=doctor.name,  # Set the doctor's name
                date=serializer.validated_data['date'],
                time=serializer.validated_data['time'],
                reason_for_visit=serializer.validated_data.get('reason_for_visit', ''),
                # Map the payment token (if provided) to payment_id;
                # mark as paid if a token exists
                payment_id=serializer.validated_data.get('payment_token', ''),
                is_paid=bool(serializer.validated_data.get('payment_token', '')),
                status='SCHEDULED'
            )

            return Response(
                AppointmentSerializer(appointment).data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel an appointment"""
        appointment = self.get_object()
        appointment.status = 'CANCELLED'
        appointment.save()

        return Response({"detail": "Appointment cancelled successfully"})

    @action(detail=True, methods=['post'])
    def reschedule(self, request, pk=None):
        """Reschedule an appointment"""
        appointment = self.get_object()

        # Get new date and time from the request
        date = request.data.get('date')
        time = request.data.get('time')

        if not date or not time:
            return Response(
                {"detail": "date and time are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        new_datetime = timezone.make_aware(
            timezone.datetime.combine(date, time)
        )

        if new_datetime <= timezone.now():
            return Response(
                {"detail": "Cannot reschedule to a past time"},
                status=status.HTTP_400_BAD_REQUEST
            )

        appointment.date = date
        appointment.time = time
        appointment.status = 'RESCHEDULED'
        appointment.save()

        return Response(AppointmentSerializer(appointment).data)

    @action(detail=True, methods=['post'])
    def mark_as_missed(self, request, pk=None):
        """Mark an appointment as missed"""
        appointment = self.get_object()
        appointment.status = 'MISSED'
        appointment.save()

        return Response({"detail": "Appointment marked as missed"})

    @action(detail=True, methods=['post'])
    def video_failed(self, request, pk=None):
        """Report that video call failed and switched to phone"""
        appointment = self.get_object()
        appointment.phone_fallback = True
        appointment.save()

        return Response({"detail": "Video failure reported"})