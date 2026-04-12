"""
Management command to link orphaned projects to mentors.
Run this after uploading CSV to link all projects at once.

Usage:
    python manage.py link_mentor_projects
    python manage.py link_mentor_projects --domain=soc
"""

import re
from django.core.management.base import BaseCommand
from django.db.models import Q
from accounts.models import UserProfile, CustomUser
from projects.models import Project, Mentor
from domains.models import Domain


class Command(BaseCommand):
    help = 'Link orphaned projects to mentors based on roll numbers in project fields'

    def add_arguments(self, parser):
        parser.add_argument(
            '--domain',
            type=str,
            help='Domain slug to process (e.g., soc, soq). If not provided, processes all domains.',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be linked without actually linking',
        )

    def handle(self, *args, **options):
        domain_slug = options.get('domain')
        dry_run = options.get('dry_run', False)

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))

        # Get projects to process
        if domain_slug:
            try:
                domain = Domain.objects.get(slug=domain_slug)
                projects = Project.objects.filter(domain=domain)
                self.stdout.write(f'Processing domain: {domain.name}')
            except Domain.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Domain "{domain_slug}" not found'))
                return
        else:
            projects = Project.objects.all()
            self.stdout.write('Processing all domains')

        total_projects = projects.count()
        self.stdout.write(f'Found {total_projects} projects')

        linked_count = 0
        already_linked_count = 0
        not_found_count = 0
        error_count = 0

        for project in projects:
            try:
                # Extract roll numbers from mentor and co_mentor_info fields
                rolls_to_link = []

                # Parse mentor field
                mentor_match = re.search(r'\((\w+)\)', project.mentor)
                if mentor_match:
                    rolls_to_link.append(mentor_match.group(1).lower())
                elif project.mentor and project.mentor.lower() != 'na':
                    # Might be just a roll number
                    rolls_to_link.append(project.mentor.strip().lower())

                # Parse co_mentor_info field
                if project.co_mentor_info and project.co_mentor_info.upper() != 'NA':
                    co_mentor_matches = re.findall(r'\((\w+)\)', project.co_mentor_info)
                    rolls_to_link.extend([r.lower() for r in co_mentor_matches])

                # Link each mentor
                for roll in rolls_to_link:
                    try:
                        user = CustomUser.objects.get(username=roll)
                        profile = UserProfile.objects.get(user=user)

                        if dry_run:
                            self.stdout.write(
                                f'  [DRY RUN] Would link {roll} to "{project.title}" in {project.domain.slug if project.domain else "legacy"}'
                            )
                            linked_count += 1
                            continue

                        # Get or create Mentor object
                        mentor_obj, created = Mentor.objects.get_or_create(
                            user=profile,
                            domain=project.domain,
                            defaults={'season': '1'}
                        )

                        # Link project
                        if project not in mentor_obj.projects.all():
                            mentor_obj.projects.add(project)
                            linked_count += 1
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'  ✓ Linked {roll} to "{project.title}" in {project.domain.slug if project.domain else "legacy"}'
                                )
                            )
                        else:
                            already_linked_count += 1
                            self.stdout.write(
                                f'  ~ {roll} already linked to "{project.title}"'
                            )

                    except CustomUser.DoesNotExist:
                        not_found_count += 1
                        self.stdout.write(
                            self.style.WARNING(
                                f'  ✗ User not found: {roll} for project "{project.title}"'
                            )
                        )
                    except UserProfile.DoesNotExist:
                        not_found_count += 1
                        self.stdout.write(
                            self.style.WARNING(
                                f'  ✗ Profile not found: {roll} for project "{project.title}"'
                            )
                        )

            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(
                        f'  ✗ Error processing project "{project.title}": {str(e)}'
                    )
                )

        # Summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('SUMMARY'))
        self.stdout.write('='*60)
        self.stdout.write(f'Total projects processed: {total_projects}')
        self.stdout.write(self.style.SUCCESS(f'Successfully linked: {linked_count}'))
        self.stdout.write(f'Already linked: {already_linked_count}')
        self.stdout.write(self.style.WARNING(f'Mentors not found: {not_found_count}'))
        self.stdout.write(self.style.ERROR(f'Errors: {error_count}'))

        if not_found_count > 0:
            self.stdout.write('\n' + self.style.WARNING(
                f'{not_found_count} mentors not found. They will be auto-linked when they first log in.'
            ))

        if dry_run:
            self.stdout.write('\n' + self.style.WARNING('DRY RUN COMPLETE - No changes were made'))
