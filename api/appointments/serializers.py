from rest_framework import serializers
from django.db import transaction


from api.doctors.models import TimeSlot
from api.payments.models import AppointmentPayment
from api.payments.choices import PaymentStatusChoices
from api.doctors.serializers import TimeSlotSerializer
from api.patients.utils.fields import LabelChoiceField
from api.patients.models import Patient
from api.patients.serializers import PatientSerializer
from api.appointments.models import Appointment
from api.appointments.choices import Status
from api.appointments.validators import (
    validate_time_slot,
)
from django.utils import timezone
import logging
import stripe

logger = logging.getLogger(__name__)


class AppointmentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Appointment model.
    This serializer is used to create appointments.
    It includes limited information.
    """

    time_slot_uuid = serializers.UUIDField(write_only=True)
    time_slot = TimeSlotSerializer(read_only=True)
    status = LabelChoiceField(
        choices=Status.choices, default=Status.PENDING, read_only=True
    )
    doctor = serializers.SerializerMethodField(read_only=True)
    visit_type = serializers.SerializerMethodField(read_only=True)

    def get_visit_type(self, obj):
        if obj.patient:
            return obj.patient.get_visit_type_display()
        return None

    def get_doctor(self, obj):
        if obj.time_slot:
            return {
                "uuid": obj.time_slot.doctor.uuid,
                "name": obj.time_slot.doctor.user.get_full_name(),
                "email": obj.time_slot.doctor.user.email,
            }
        return None

    def validate(self, data):
        time_slot_uuid = data.get("time_slot_uuid")
        validate_time_slot(self, time_slot_uuid)

        return data

    class Meta:
        model = Appointment
        fields = [
            "uuid",
            "doctor",
            "time_slot_uuid",
            "time_slot",
            "visit_type",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "uuid",
            "doctor",
            "time_slot",
            "status",
            "visit_type",
            "created_at",
            "updated_at",
        ]

    @transaction.atomic
    def create(self, validated_data):
        try:
            request = self.context["request"]
            patient = Patient.objects.get(user=request.user)
            validated_data["patient"] = patient
            time_slot_uuid = validated_data.pop("time_slot_uuid")
            # mark the time slot as booked
            time_slot = TimeSlot.objects.get(uuid=time_slot_uuid)
            validated_data["time_slot"] = time_slot
            time_slot.is_booked = True
            time_slot.save()
            return super().create(validated_data)

        except Patient.DoesNotExist:
            raise serializers.ValidationError("Patient profile not found for this user")

        except Exception as e:
            raise serializers.ValidationError(f"Error creating appointment: {str(e)}")


class AppointmentDetailSerializer(AppointmentSerializer):
    """
    Serializer for the Appointment model with detailed information.
    This serializer is used to retrieve appointment details.
    It includes the time slot and patient information.
    """

    patient = PatientSerializer(read_only=True)

    class Meta(AppointmentSerializer.Meta):
        fields = AppointmentSerializer.Meta.fields + ["patient"]
        read_only_fields = AppointmentSerializer.Meta.read_only_fields


class DoctorAppointmentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Appointment model for doctors.
    This serializer is used to retrieve appointments for a doctor.
    It includes the time slot and patient information.
    """

    time_slot = TimeSlotSerializer(read_only=True)
    patient = serializers.SerializerMethodField(read_only=True)
    doctor = serializers.SerializerMethodField(read_only=True)
    status = serializers.SerializerMethodField(read_only=True)

    def get_status(self, obj):
        return obj.get_status_display()

    def get_doctor(self, obj):
        if obj.time_slot:
            return {
                "doctor": obj.time_slot.doctor.user.get_full_name(),
            }
        return None

    def get_patient(self, obj):
        if obj.patient:
            return {
                "first_name": obj.patient.user.first_name,
                "middle_name": obj.patient.user.middle_name,
                "last_name": obj.patient.user.last_name,
                "visit_type": obj.patient.get_visit_type_display(),
                "state": obj.patient.state,
                "gender": obj.patient.get_gender_display(),
            }
        return None

    class Meta:
        model = Appointment
        fields = [
            "uuid",
            "time_slot",
            "doctor",
            "patient",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "uuid",
            "time_slot",
            "patient",
            "doctor",
            "status",
            "created_at",
            "updated_at",
        ]


class RescheduleAppointmentSerializer(serializers.ModelSerializer):
    """
    Serializer for rescheduling an Appointment.
    """
    new_time_slot_uuid = serializers.UUIDField(write_only=True)
    reschedule_message = serializers.CharField(read_only=True)  
    status = LabelChoiceField(choices=Status.choices, default=Status.CONFIRMED, read_only=True)
    doctor = serializers.SerializerMethodField(read_only=True)
    visit_type = serializers.SerializerMethodField(read_only=True)

    def get_visit_type(self, obj):
        if obj.patient:
            return obj.patient.get_visit_type_display()
        return None

    def get_doctor(self, obj):
        if obj.time_slot:
            return {
                "uuid": obj.time_slot.doctor.uuid,
                "name": obj.time_slot.doctor.user.get_full_name(),
                "email": obj.time_slot.doctor.user.email,
            }
        return None

    def validate(self, data):
        new_time_slot_uuid = data.get("new_time_slot_uuid")
        appointment = self.instance
        current_time = timezone.now()
        time_diff = (appointment.time_slot.start_time - current_time).total_seconds() / 3600

        # Policy 1: 0–4 hours before - No rescheduling allowed
        if time_diff < 4:
            logger.info(f"Rescheduling attempt denied for appointment {appointment.uuid}: Within 4 hours")
            raise serializers.ValidationError("Rescheduling not allowed within 4 hours")
            
        if not TimeSlot.objects.filter(uuid=new_time_slot_uuid, is_booked=False).exists():
            raise serializers.ValidationError("New time slot is not available")

        # Policy 2: 4–24 hours before - 50% fee of original cost
        if 4 <= time_diff <= 24:
            payment = AppointmentPayment.objects.filter(appointment=appointment, status=PaymentStatusChoices.SUCCEEDED).first()
            if not payment:
                logger.error(f"No original payment found for appointment {appointment.uuid}")
                raise serializers.ValidationError("Original payment not found")
            original_amount = payment.amount
            reschedule_fee = original_amount * 0.5  # 50% of original amount
            data['reschedule_fee_required'] = reschedule_fee  # Required for 4–24 hours scenario
            logger.info(f"Rescheduling approved for appointment {appointment.uuid} with {reschedule_fee} fee")


        # Policy 3: More than 24 hours before - No additional fee
        
        elif time_diff > 24:
            logger.info(f"Rescheduling approved for appointment {appointment.uuid}: No additional fee required")
            data['reschedule_message'] = "You can reschedule this appointment"  # Set the message
         
        return data

    @transaction.atomic
    def update(self, instance, validated_data):
        new_time_slot_uuid = validated_data.pop("new_time_slot_uuid")
        new_time_slot = TimeSlot.objects.get(uuid=new_time_slot_uuid)
        
        # Update time slot
        instance.time_slot.is_booked = False
        instance.time_slot.save()
        new_time_slot.is_booked = True
        new_time_slot.save()
        instance.time_slot = new_time_slot

        if 'reschedule_fee_required' in validated_data:
            fee = validated_data['reschedule_fee_required']
            payment_intent = stripe.PaymentIntent.create(
                amount=int(fee * 100),
                currency='usd',
                metadata={"appointment_uuid": str(instance.uuid)},
                automatic_payment_methods={"enabled": True},
            )
            instance.reschedule_fee_paid = fee
            # Save payment intent
            AppointmentPayment.objects.create(
                stripe_payment_intent_id=payment_intent.id,
                stripe_client_secret=payment_intent.client_secret,
                amount=fee,
                currency='usd',
                status=PaymentStatusChoices.REQUIRES_PAYMENT_METHOD,
                patient=instance.patient,
                appointment=instance
            )
            logger.info(f"Payment intent created for rescheduling appointment {instance.uuid} with fee {fee}")

        instance.status = Status.RESCHEDULED
        instance.save()
        return instance

    class Meta:
        model = Appointment
        fields = [
            "uuid",
            "doctor",
            "new_time_slot_uuid",
            "time_slot",
            "visit_type",
            "status",
            "reschedule_fee_paid",
            "reschedule_message",  
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "uuid",
            "doctor",
            "time_slot",
            "visit_type",
            "status",
            "reschedule_message",  
            "created_at",
            "updated_at",
        ]   
        
