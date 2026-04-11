import json
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django_tenants.utils import tenant_context

from apps.organizations.enums import Role
from apps.organizations.models import Membership
from apps.organizations.models import Organization
from apps.users.models import User


class Command(BaseCommand):
    help = "Seed the database with fixture data, creating organization schemas as needed."

    def handle(self, *args, **options):
        fixtures_dir = Path(settings.BASE_DIR) / "fixtures"

        # 1. Load users
        self.stdout.write("Loading users...")
        call_command("loaddata", str(fixtures_dir / "users.json"))

        # 2. Create organizations via ORM (triggers schema creation)
        self.stdout.write("Creating organizations...")
        orgs_file = fixtures_dir / "organizations.json"
        orgs_data = json.loads(orgs_file.read_text())

        for entry in orgs_data:
            fields = entry["fields"]
            org, created = Organization.objects.get_or_create(
                pk=entry["pk"],
                defaults={
                    "schema_name": fields["schema_name"],
                    "name": fields["name"],
                },
            )
            if created:
                self.stdout.write(f"  Created organization: {org}")
            else:
                self.stdout.write(f"  Already exists: {org}")

            # Create memberships
            for membership_data in fields.get("memberships", []):
                user = User.objects.get(pk=membership_data["user"])
                Membership.objects.get_or_create(
                    user=user,
                    organization=org,
                    defaults={
                        "role": membership_data.get("role", Role.MEMBER),
                        "is_default": membership_data.get("is_default", False),
                    },
                )
                self.stdout.write(f"    {user} -> {org} ({membership_data.get('role', 'member')})")

        # 3. Load organization-specific data
        for org in Organization.objects.all():
            fixture_file = fixtures_dir / f"{org.schema_name}.json"
            if fixture_file.exists():
                self.stdout.write(f"Loading data for {org.schema_name}...")
                with tenant_context(org):
                    call_command("loaddata", str(fixture_file))
            else:
                self.stdout.write(f"  No fixture found for {org.schema_name}, skipping.")

        self.stdout.write(self.style.SUCCESS("Seed complete."))
