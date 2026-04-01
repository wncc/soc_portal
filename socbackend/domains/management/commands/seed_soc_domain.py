"""
Management command: seed_soc_domain

Migrates all existing SOC portal data to the new multi-domain architecture:
  1. Creates the canonical 'soc' Domain
  2. Assigns all existing Projects to the soc domain
  3. Assigns all existing Mentor/Mentee objects to the soc domain
  4. Creates DomainMembership records from existing Mentor/Mentee objects
  5. Consolidates duplicate CustomUser rows (same roll number, different role)
     into a single user + DomainMembership rows for backward compat

Run once after migrations:
  python manage.py seed_soc_domain
"""

from django.core.management.base import BaseCommand
from django.db import transaction


class Command(BaseCommand):
    help = "Seeds the SOC domain and migrates all existing data to the multi-domain schema"

    def handle(self, *args, **options):
        # Import here to avoid circular import issues at module load time
        from domains.models import Domain, DomainMembership
        from projects.models import Mentor, Mentee, Project
        from accounts.models import CustomUser, UserProfile

        self.stdout.write(self.style.MIGRATE_HEADING("=== seed_soc_domain ==="))

        with transaction.atomic():
            # ----------------------------------------------------------------
            # Step 1: Create the canonical SOC domain
            # ----------------------------------------------------------------
            soc, created = Domain.objects.get_or_create(
                slug="soc",
                defaults={
                    "name": "Summer of Code",
                    "description": (
                        "Summer of Code (SOC) is WnCC's flagship program that "
                        "connects IIT Bombay students with exciting coding projects "
                        "mentored by seniors and alumni."
                    ),
                    "is_active": True,
                    "order": 0,
                },
            )
            if created:
                self.stdout.write(self.style.SUCCESS("  ✓ Created Domain: Summer of Code (soc)"))
            else:
                self.stdout.write(self.style.WARNING("  ~ Domain 'soc' already exists, skipping creation"))

            # ----------------------------------------------------------------
            # Step 2: Assign all existing Projects to soc domain (if not already)
            # ----------------------------------------------------------------
            projects_updated = Project.objects.filter(domain__isnull=True).update(domain=soc)
            self.stdout.write(self.style.SUCCESS(f"  ✓ Assigned {projects_updated} Projects to 'soc' domain"))

            # ----------------------------------------------------------------
            # Step 3: Assign all existing Mentor objects to soc domain
            # ----------------------------------------------------------------
            mentors_updated = Mentor.objects.filter(domain__isnull=True).update(domain=soc)
            self.stdout.write(self.style.SUCCESS(f"  ✓ Assigned {mentors_updated} Mentor objects to 'soc' domain"))

            # ----------------------------------------------------------------
            # Step 4: Assign all existing Mentee objects to soc domain
            # ----------------------------------------------------------------
            mentees_updated = Mentee.objects.filter(domain__isnull=True).update(domain=soc)
            self.stdout.write(self.style.SUCCESS(f"  ✓ Assigned {mentees_updated} Mentee objects to 'soc' domain"))

            # ----------------------------------------------------------------
            # Step 5: Create DomainMembership rows from existing Mentor/Mentee objects
            # ----------------------------------------------------------------
            membership_created = 0

            for mentor in Mentor.objects.select_related("user__user").all():
                user = mentor.user.user  # UserProfile -> CustomUser
                _, c = DomainMembership.objects.get_or_create(
                    user=user, domain=soc, role="mentor",
                    defaults={"is_approved": True},
                )
                if c:
                    membership_created += 1

            for mentee in Mentee.objects.select_related("user__user").all():
                user = mentee.user.user
                _, c = DomainMembership.objects.get_or_create(
                    user=user, domain=soc, role="mentee",
                    defaults={"is_approved": True},
                )
                if c:
                    membership_created += 1

            self.stdout.write(self.style.SUCCESS(f"  ✓ Created {membership_created} DomainMembership records"))

            # ----------------------------------------------------------------
            # Step 6: Consolidate duplicate CustomUser rows
            # Users can exist as (roll, 'mentee') AND (roll, 'mentor') — deduplicate
            # ----------------------------------------------------------------
            self.stdout.write(self.style.MIGRATE_HEADING("\n  Consolidating duplicate CustomUser rows..."))

            usernames = CustomUser.objects.values_list("username", flat=True).distinct()
            consolidated = 0

            for username in usernames:
                users = CustomUser.objects.filter(username=username).order_by("id")
                if users.count() <= 1:
                    continue

                # Keep the oldest user record as canonical
                canonical = users.first()
                duplicates = users.exclude(id=canonical.id)

                for dup in duplicates:
                    # Transfer UserProfile if canonical doesn't have one
                    if not UserProfile.objects.filter(user=canonical).exists():
                        try:
                            profile = UserProfile.objects.get(user=dup)
                            profile.user = canonical
                            profile.save()
                        except UserProfile.DoesNotExist:
                            pass

                    # Transfer Mentor
                    Mentor.objects.filter(user__user=dup).update(user=UserProfile.objects.filter(user=canonical).first())
                    # Transfer Mentee
                    Mentee.objects.filter(user__user=dup).update(user=UserProfile.objects.filter(user=canonical).first())
                    # Transfer DomainMemberships
                    for dm in DomainMembership.objects.filter(user=dup):
                        DomainMembership.objects.get_or_create(
                            user=canonical, domain=dm.domain, role=dm.role,
                            defaults={"is_approved": dm.is_approved},
                        )
                        dm.delete()

                    dup.delete()
                    consolidated += 1

            self.stdout.write(self.style.SUCCESS(f"  ✓ Consolidated {consolidated} duplicate CustomUser rows"))

        self.stdout.write(self.style.SUCCESS("\n✅ seed_soc_domain completed successfully"))
