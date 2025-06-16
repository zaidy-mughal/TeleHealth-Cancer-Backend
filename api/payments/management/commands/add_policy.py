from django.core.management.base import BaseCommand
from api.payments.models import RefundPolicy
from api.payments.choices import RefundPolicyChoices


class Command(BaseCommand):
    help = "Add default refund policies for appointment payments"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Force creation of policies even if they already exist",
        )

    def handle(self, *args, **options):
        force = options.get("force", False)

        # Check if policies already exist
        existing_policies = RefundPolicy.objects.filter(is_active=True).count()

        if existing_policies > 0 and not force:
            self.stdout.write(
                self.style.WARNING(
                    f"Found {existing_policies} existing active policies. "
                    "Use --force to recreate them."
                )
            )
            return

        if force and existing_policies > 0:
            # Delete existing policies
            RefundPolicy.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(f"Deactivated {existing_policies} existing policies")
            )

        policies = [
            {
                "name": "No Refund Policy",
                "refund_type": RefundPolicyChoices.NO_REFUND,
                "hours_before_min": 0,
                "hours_before_max": 4,
                "refund_percentage": 0.00,
                "description": "0% refund for cancellations 0-4 hours before appointment",
            },
            {
                "name": "Partial Refund Policy",
                "refund_type": RefundPolicyChoices.PARTIAL_REFUND,
                "hours_before_min": 4,
                "hours_before_max": 24,
                "refund_percentage": 50.00,
                "description": "50% refund for cancellations 4-24 hours before appointment",
            },
            {
                "name": "Full Refund Policy",
                "refund_type": RefundPolicyChoices.FULL_REFUND,
                "hours_before_min": 24,
                "hours_before_max": 99999,
                "refund_percentage": 100.00,
                "description": "100% refund for cancellations 24+ hours before appointment",
            },
        ]

        created_count = 0

        for policy_data in policies:
            description = policy_data.pop("description")

            try:
                policy, created = RefundPolicy.objects.get_or_create(
                    name=policy_data["name"],
                    defaults={**policy_data, "is_active": True},
                )

                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"✓ Created: {policy.name} - {description}")
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f"Policy {policy.name} Skipped.")
                    )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ Error creating {policy_data["name"]}: {str(e)}'
                    )
                )

        # Summary
        if created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nSuccessfully created {created_count} refund policies!"
                )
            )
        else:
            self.stdout.write(self.style.WARNING("\nNo new policies were created."))

        # Display current active policies
        self.stdout.write("\nCurrent active refund policies:")
        for policy in RefundPolicy.objects.filter(is_active=True).order_by(
            "hours_before_min"
        ):
            if policy.hours_before_max:
                range_text = (
                    f"{policy.hours_before_min}-{policy.hours_before_max} hours"
                )
            else:
                range_text = f"{policy.hours_before_min}+ hours"

            self.stdout.write(
                f"  • {policy.name}: {policy.refund_percentage}% ({range_text})"
            )
