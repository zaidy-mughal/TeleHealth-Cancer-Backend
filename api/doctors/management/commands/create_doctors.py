# api/doctors/management/commands/create_doctors.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
import random
import string
import logging

from api.doctors.models import Doctor, LicenseInfo, Service, DoctorService, Specialization
from api.doctors.choices import Services, StateChoices
from api.users.choices import Role  # Import Role enum

logger = logging.getLogger(__name__)

User = get_user_model()  # Use the custom user model

# List of U.S. state abbreviations (aligned with StateChoices labels)
US_STATES = [choice.label for choice in StateChoices]

# Service abbreviations for email generation
SERVICE_ABBRS = {
    Services.SURVEILLANCE: 'sur',
    Services.DIAGNOSIS: 'dia',
    Services.SCREENING: 'scr',
    Services.SECOND_OPINION: 'sop'
}

# Generate a random name
def generate_name():
    first_names = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Emily', 'Robert', 'Lisa']
    last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis']
    return f"{random.choice(first_names)} {random.choice(last_names)}"

# Generate a random NPI number (10 digits, for demo)
def generate_npi():
    return ''.join(random.choices(string.digits, k=10))

# Generate a unique license number (state code + 7-digit number)
def generate_license_number(state):
    state_abbr = next((k for k, v in StateChoices.choices if v == state), state[:2].upper())
    return f"{state_abbr}-{''.join(random.choices(string.digits, k=7))}"

class Command(BaseCommand):
    help = 'Creates doctor accounts for all U.S. states with different services'

    @transaction.atomic
    def handle(self, *args, **options):
        counter = 1
        for state in US_STATES:
            for service_value, service_name in Services.choices:
                # Generate unique email and password
                email = f"dr-{state.replace(' ', '-').lower()}-{SERVICE_ABBRS[service_value]}-{str(counter).zfill(3)}@curuth.com"
                password = email.replace('@curuth.com', '')  # Password matches email without domain
                full_name = generate_name()
                first_name, last_name = full_name.split()

                # Create user with role=Role.DOCTOR (1)
                try:
                    user = User.objects.create_user(
                        email=email,
                        password=password,
                        first_name=first_name,
                        last_name=last_name,
                        role=Role.DOCTOR,  # Set role to Doctor (1)
                        is_email_verified=False  # Optional, based on your model
                    )
                    logger.info(f"Successfully created user {email}")
                except Exception as e:
                    logger.error(f"Failed to create user {email}: {str(e)}")
                    continue  # Skip to next iteration on user creation failure

                # Create specialization if it doesn't exist
                specialization_name = f"{service_name} Specialist"
                specialization, _ = Specialization.objects.get_or_create(name=specialization_name)

                # Create doctor
                try:
                    doctor = Doctor.objects.create(
                        user=user,
                        specialization=specialization,
                        date_of_birth=timezone.now().date(),
                        address=f"123 Main St, {state} City, {state} 12345",
                        npi_number=generate_npi()
                    )
                    logger.info(f"Successfully created doctor for {email}")
                except Exception as e:
                    logger.error(f"Failed to create doctor for {email}: {str(e)}")
                    user.delete()  # Attempt to clean up user, but let transaction handle rollback
                    continue  # Skip to next iteration on doctor creation failure

                # Create service if it doesn't exist
                service, _ = Service.objects.get_or_create(name=service_value)

                # Create DoctorService relationship
                DoctorService.objects.get_or_create(doctor=doctor, service=service)

                # Create license info with correct state value
                state_value = next((k for k, v in StateChoices.choices if v == state), StateChoices.ALABAMA)
                try:
                    LicenseInfo.objects.create(
                        doctor=doctor,
                        license_number=generate_license_number(state),
                        state=state_value  # Use the integer value from StateChoices
                    )
                    logger.info(f"Successfully created license for {email}")
                except Exception as e:
                    logger.error(f"Failed to create license for {email}: {str(e)}")
                    # Avoid further deletes; let transaction rollback
                    continue

                self.stdout.write(
                    self.style.SUCCESS(f"Created doctor: {full_name} ({email}) with password {password}, "
                                     f"license {doctor.license_info.first().license_number}, "
                                     f"service {service_name} in {state}")
                )
                counter += 1

if __name__ == "__main__":
    from django.core.management import execute_from_command_line
    execute_from_command_line(["manage.py", "create_doctors"])