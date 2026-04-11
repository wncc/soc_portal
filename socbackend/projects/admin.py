"""
projects/admin.py  —  Summer of Tech admin for Projects, Mentors, Mentees, RankList

Key upgrades over the old admin:
  - Domain-aware filters everywhere (filter by domain slug)
  - Mentor/Mentee show domain column + are filterable by domain
  - RankList is now per-project (no mentor FK) — export uses the unified list
  - Co-mentor linking action updated to work without role field
  - All list pages support 1000+ rows
  - CSV exports preserved and improved
"""

import csv
import io
import re
import zipfile
from collections import defaultdict
from statistics import mean

from django.contrib import admin
from django.db import models as dj_models
from django.http import HttpResponse

from accounts.models import UserProfile, CustomUser
from .models import (
    Mentee, MenteePreference, MenteeWishlist,
    Mentor, Project, RankList,
)


# ===========================================================================
# Inline helpers
# ===========================================================================

class MenteePreferenceInline(admin.TabularInline):
    model = MenteePreference
    extra = 0
    readonly_fields = ('mentee', 'project', 'preference', 'sop')
    can_delete = False
    show_change_link = True


class RankListInline(admin.TabularInline):
    """Shows the project-level ranklist directly inside a Project."""
    model = RankList
    extra = 0
    fields = ('mentee_roll', 'mentee_name', 'rank', 'preference')
    readonly_fields = ('mentee_roll', 'mentee_name', 'rank', 'preference')
    can_delete = False
    ordering = ('rank',)

    def mentee_roll(self, obj):
        return obj.mentee.user.roll_number
    mentee_roll.short_description = 'Roll No'

    def mentee_name(self, obj):
        return obj.mentee.user.name
    mentee_name.short_description = 'Name'


# ===========================================================================
# Project Admin
# ===========================================================================

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'domain_slug', 'general_category', 'specific_category',
        'mentee_max', 'mentor_names', 'co_mentor_names_display',
    )
    search_fields = ('title', 'mentor', 'co_mentor_info')
    list_filter = ('domain', 'general_category')
    list_per_page = 1000
    inlines = [RankListInline]
    actions = ['export_projects_csv', 'add_co_mentor_as_mentor', 'clear_banner_images']

    # ---- Computed columns ----

    def domain_slug(self, obj):
        return obj.domain.slug.upper() if obj.domain else '—'
    domain_slug.short_description = 'Domain'
    domain_slug.admin_order_field = 'domain__slug'

    def mentor_names(self, obj):
        mentors = Mentor.objects.filter(projects=obj).select_related('user')
        names = [f'{m.user.name} ({m.user.roll_number})' for m in mentors]
        return ', '.join(names) if names else '—'
    mentor_names.short_description = 'Mentors'

    def co_mentor_names_display(self, obj):
        if not obj.co_mentor_info or obj.co_mentor_info == 'NA':
            return '—'
        matches = re.findall(r'([A-Za-z\s]+)\s\((\w+)\)', obj.co_mentor_info)
        return ', '.join(f'{n.strip()} ({r})' for n, r in matches) if matches else obj.co_mentor_info[:60]
    co_mentor_names_display.short_description = 'Co-Mentors'

    # ---- Actions ----

    @admin.action(description='Export selected projects to CSV')
    def export_projects_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="projects.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Domain', 'Title', 'General Category', 'Specific Category',
            'Mentee Max', 'Mentor Names', 'Mentor Rolls',
            'Co-Mentor Names', 'Co-Mentor Rolls', 'Co-Mentor Info',
            'Weekly Meets', 'Description', 'Timeline', 'Checkpoints',
            'Prerequisites', 'Banner Image Link', 'Code',
        ])
        for p in queryset.select_related('domain'):
            mentors = Mentor.objects.filter(projects=p).select_related('user')
            mentor_names = ', '.join(m.user.name for m in mentors) or '—'
            mentor_rolls = ', '.join(m.user.roll_number for m in mentors) or '—'
            co_matches = re.findall(r'([A-Za-z\s]+)\s\((\w+)\)', p.co_mentor_info or '')
            co_names = ', '.join(n.strip() for n, _ in co_matches) or '—'
            co_rolls = ', '.join(r for _, r in co_matches) or '—'
            writer.writerow([
                p.id, p.domain.slug if p.domain else '',
                p.title, p.general_category, p.specific_category, p.mentee_max,
                mentor_names, mentor_rolls, co_names, co_rolls, p.co_mentor_info,
                p.weekly_meets, p.description, p.timeline,
                p.checkpoints, p.prereuisites, p.banner_image_link, p.code,
            ])
        return response

    @admin.action(description='Link co-mentors listed in co_mentor_info as project mentors')
    def add_co_mentor_as_mentor(self, request, queryset):
        """
        Updated for new architecture: no role field on CustomUser.
        Looks up UserProfile by roll number and links to Mentor in same domain.
        """
        for project in queryset.select_related('domain'):
            if not project.co_mentor_info or project.co_mentor_info == 'NA':
                continue
            matches = re.findall(r'([A-Za-z\s]+)\s\((\w+)\)', project.co_mentor_info)
            for name, roll_number in matches:
                roll_number = roll_number.strip().lower()
                try:
                    user = CustomUser.objects.get(username=roll_number)
                    profile = UserProfile.objects.get(user=user)
                    # Find or create mentor record in the same domain
                    mentor, created = Mentor.objects.get_or_create(
                        user=profile,
                        domain=project.domain,
                        defaults={'season': '1'},
                    )
                    if project not in mentor.projects.all():
                        mentor.projects.add(project)
                        self.message_user(
                            request,
                            f'✓ Co-mentor {name.strip()} ({roll_number}) linked to "{project.title}".'
                        )
                    else:
                        self.message_user(
                            request,
                            f'~ {name.strip()} already linked to "{project.title}".'
                        )
                except CustomUser.DoesNotExist:
                    self.message_user(request, f'✗ No user found for roll: {roll_number}')
                except UserProfile.DoesNotExist:
                    self.message_user(request, f'✗ No profile found for roll: {roll_number}')
        self.message_user(request, 'Co-mentor linking complete.')

    @admin.action(description='Clear banner images for selected projects')
    def clear_banner_images(self, request, queryset):
        queryset.update(banner_image=None)
        self.message_user(request, f'Cleared banner images for {queryset.count()} projects.')


# ===========================================================================
# Mentor Admin
# ===========================================================================

@admin.register(Mentor)
class MentorAdmin(admin.ModelAdmin):
    list_display = (
        'mentor_name', 'roll_number', 'phone_number', 'domain_slug', 'season',
        'project_count', 'project_list',
    )
    search_fields = ('user__name', 'user__roll_number', 'user__phone_number')
    list_filter = ('domain', 'season')
    list_per_page = 1000
    actions = ['export_mentors_csv']

    def get_queryset(self, request):
        return (
            super().get_queryset(request)
            .select_related('user', 'domain')
            .prefetch_related('projects')
            .annotate(_project_count=dj_models.Count('projects'))
        )

    def mentor_name(self, obj):
        return obj.user.name
    mentor_name.short_description = 'Name'
    mentor_name.admin_order_field = 'user__name'

    def roll_number(self, obj):
        return obj.user.roll_number
    roll_number.short_description = 'Roll No'
    roll_number.admin_order_field = 'user__roll_number'

    def phone_number(self, obj):
        return obj.user.phone_number
    phone_number.short_description = 'Phone'
    phone_number.admin_order_field = 'user__phone_number'

    def domain_slug(self, obj):
        return obj.domain.slug.upper() if obj.domain else '—'
    domain_slug.short_description = 'Domain'
    domain_slug.admin_order_field = 'domain__slug'

    def project_count(self, obj):
        return obj._project_count
    project_count.short_description = '# Projects'
    project_count.admin_order_field = '_project_count'

    def project_list(self, obj):
        titles = [p.title for p in obj.projects.all()]
        return '; '.join(titles) if titles else '—'
    project_list.short_description = 'Projects'

    @admin.action(description='Export selected mentors to CSV')
    def export_mentors_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="mentors.csv"'
        writer = csv.writer(response)
        writer.writerow(['Roll No', 'Name', 'Phone', 'Domain', 'Season', '# Projects', 'Projects'])
        for m in queryset.select_related('user', 'domain').prefetch_related('projects'):
            writer.writerow([
                m.user.roll_number, m.user.name, m.user.phone_number,
                m.domain.slug if m.domain else '',
                m.season,
                m.projects.count(),
                '; '.join(p.title for p in m.projects.all()),
            ])
        return response


# ===========================================================================
# Mentee Admin
# ===========================================================================

@admin.register(Mentee)
class MenteeAdmin(admin.ModelAdmin):
    list_display = (
        'mentee_name', 'roll_number', 'domain_slug', 'season',
        'pref_count', 'assigned_projects',
    )
    search_fields = ('user__name', 'user__roll_number')
    list_filter = ('domain', 'season')
    list_per_page = 1000
    inlines = [MenteePreferenceInline]
    actions = ['export_mentees_csv']

    def get_queryset(self, request):
        return (
            super().get_queryset(request)
            .select_related('user', 'domain')
            .annotate(_pref_count=dj_models.Count('menteepreference'))
        )

    def mentee_name(self, obj):
        return obj.user.name
    mentee_name.short_description = 'Name'
    mentee_name.admin_order_field = 'user__name'

    def roll_number(self, obj):
        return obj.user.roll_number
    roll_number.short_description = 'Roll No'
    roll_number.admin_order_field = 'user__roll_number'

    def domain_slug(self, obj):
        return obj.domain.slug.upper() if obj.domain else '—'
    domain_slug.short_description = 'Domain'
    domain_slug.admin_order_field = 'domain__slug'

    def pref_count(self, obj):
        return obj._pref_count
    pref_count.short_description = 'Preferences'
    pref_count.admin_order_field = '_pref_count'

    def assigned_projects(self, obj):
        """Show projects this mentee was selected for (appears in any ranklist)."""
        ranks = RankList.objects.filter(mentee=obj).select_related('project')
        if not ranks:
            return '—'
        return ' | '.join(f'{r.project.title} (rank #{r.rank})' for r in ranks)
    assigned_projects.short_description = 'In Ranklist'

    @admin.action(description='Export selected mentees to CSV')
    def export_mentees_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="mentees.csv"'
        writer = csv.writer(response)
        writer.writerow(['Roll No', 'Name', 'Domain', 'Season', '# Preferences'])
        for m in queryset.select_related('user', 'domain'):
            writer.writerow([
                m.user.roll_number, m.user.name,
                m.domain.slug if m.domain else '',
                m.season,
                MenteePreference.objects.filter(mentee=m).count(),
            ])
        return response


# ===========================================================================
# MenteePreference Admin
# ===========================================================================

@admin.register(MenteePreference)
class MenteePreferencesAdmin(admin.ModelAdmin):
    list_display = ('mentee_roll', 'mentee_name', 'domain_slug', 'project', 'preference')
    search_fields = ('mentee__user__roll_number', 'mentee__user__name', 'project__title')
    list_filter = ('preference', 'mentee__domain')
    list_per_page = 1000
    actions = ['export_preferences_csv', 'count_unique_mentees']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'mentee__user', 'mentee__domain', 'project'
        )

    def mentee_roll(self, obj):
        return obj.mentee.user.roll_number
    mentee_roll.short_description = 'Roll No'
    mentee_roll.admin_order_field = 'mentee__user__roll_number'

    def mentee_name(self, obj):
        return obj.mentee.user.name
    mentee_name.short_description = 'Name'

    def domain_slug(self, obj):
        return obj.mentee.domain.slug.upper() if obj.mentee.domain else '—'
    domain_slug.short_description = 'Domain'

    @admin.action(description='Export selected preferences to CSV')
    def export_preferences_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="mentee_preferences_summary.csv"'
        writer = csv.writer(response)
        header = ['Mentee Roll No', 'Mentee Name', 'Domain']
        for i in range(1, 4):
            header.extend([f'Project {i} Title', f'ID {i}', f'Pref {i}'])
        writer.writerow(header)

        # Group by mentee
        mentee_pref_map = defaultdict(list)
        for pref in queryset:
            mentee_pref_map[pref.mentee_id].append(pref)

        for mentee_id, prefs in mentee_pref_map.items():
            prefs_sorted = sorted(prefs, key=lambda x: x.preference)[:3]
            m = prefs_sorted[0].mentee
            domain = m.domain.slug if m.domain else ''
            row = [m.user.roll_number, m.user.name, domain]
            for p in prefs_sorted:
                row.extend([p.project.title, p.project.id, p.preference])
            # Pad to 3 prefs
            while len(row) < 3 + 3 * 3:
                row.extend(['', '', ''])
            writer.writerow(row)

        # Project summary
        writer.writerow([])
        writer.writerow(['--- Project Summary ---'])
        writer.writerow(['Project ID', 'Project Title', 'Domain', 'Unique Applicants', 'Max Mentees'])
        project_counts = defaultdict(set)
        for pref in queryset:
            project_counts[pref.project_id].add(pref.mentee_id)
        for pid, mentee_set in project_counts.items():
            try:
                p = Project.objects.select_related('domain').get(id=pid)
                writer.writerow([
                    pid, p.title,
                    p.domain.slug if p.domain else '',
                    len(mentee_set), p.mentee_max,
                ])
            except Project.DoesNotExist:
                pass
        return response

    @admin.action(description='Count unique mentees in selected preferences')
    def count_unique_mentees(self, request, queryset):
        count = queryset.values_list('mentee_id', flat=True).distinct().count()
        self.message_user(request, f'{count} unique mentees in the selected preferences.')


# ===========================================================================
# MenteeWishlist Admin
# ===========================================================================

@admin.register(MenteeWishlist)
class MenteeWishlistAdmin(admin.ModelAdmin):
    list_display = ('mentee_roll', 'mentee_name', 'project', 'domain_slug')
    search_fields = ('mentee__user__roll_number', 'mentee__user__name', 'project__title')
    list_filter = ('mentee__domain',)
    list_per_page = 1000

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('mentee__user', 'mentee__domain', 'project')

    def mentee_roll(self, obj):
        return obj.mentee.user.roll_number
    mentee_roll.short_description = 'Roll No'

    def mentee_name(self, obj):
        return obj.mentee.user.name
    mentee_name.short_description = 'Name'

    def domain_slug(self, obj):
        return obj.mentee.domain.slug.upper() if obj.mentee.domain else '—'
    domain_slug.short_description = 'Domain'


# ===========================================================================
# RankList Admin  —  THE BIG ONE
# Preserved from original and upgraded for the new per-project ranklist.
# ===========================================================================

@admin.register(RankList)
class RankListAdmin(admin.ModelAdmin):
    list_display = (
        'project_title', 'domain_slug', 'mentee_roll', 'mentee_name',
        'rank', 'preference', 'mentor_names_for_project',
    )
    search_fields = (
        'project__title', 'mentee__user__roll_number', 'mentee__user__name'
    )
    list_filter = ('project__domain', 'preference', 'rank')
    list_per_page = 1000
    ordering = ('project', 'rank')
    actions = ['export_ranklist_csv', 'generate_final_selection']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'project__domain', 'mentee__user', 'mentee__domain'
        )

    def project_title(self, obj):
        return obj.project.title
    project_title.short_description = 'Project'
    project_title.admin_order_field = 'project__title'

    def domain_slug(self, obj):
        return obj.project.domain.slug.upper() if obj.project.domain else '—'
    domain_slug.short_description = 'Domain'

    def mentee_roll(self, obj):
        return obj.mentee.user.roll_number
    mentee_roll.short_description = 'Mentee Roll'

    def mentee_name(self, obj):
        return obj.mentee.user.name
    mentee_name.short_description = 'Mentee Name'

    def mentor_names_for_project(self, obj):
        mentors = Mentor.objects.filter(projects=obj.project).select_related('user')
        return ', '.join(m.user.name for m in mentors) or '—'
    mentor_names_for_project.short_description = 'Mentors'

    # -------------------------------------------------------------------------
    # Export raw ranklist CSV
    # -------------------------------------------------------------------------
    @admin.action(description='Export selected rank entries to CSV')
    def export_ranklist_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="ranklist.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'Domain', 'Project ID', 'Project Title',
            'Mentor Names', 'Mentor Rolls',
            'Mentee Roll', 'Mentee Name', 'Rank', 'Preference',
        ])
        for entry in queryset.select_related('project__domain', 'mentee__user'):
            mentors = Mentor.objects.filter(projects=entry.project).select_related('user')
            writer.writerow([
                entry.project.domain.slug if entry.project.domain else '',
                entry.project.id, entry.project.title,
                ', '.join(m.user.name for m in mentors),
                ', '.join(m.user.roll_number for m in mentors),
                entry.mentee.user.roll_number, entry.mentee.user.name,
                entry.rank, entry.preference,
            ])
        return response

    # -------------------------------------------------------------------------
    # Generate final selection ZIP
    # (preserved from original, updated for no-mentor-FK ranklist)
    # -------------------------------------------------------------------------
    @admin.action(description='Generate final mentee selection (ZIP with 3 CSVs)')
    def generate_final_selection(self, request, queryset):
        """
        For each project in the selected ranklist entries:
          1. Aggregate ranks across all mentors (now trivial — no dedup needed)
          2. Sort by: frequency (desc), avg_rank (asc), best_preference (asc)
          3. Assign mentees by preference round (pref 1 first, then 2, then 3)
          4. Output ZIP: selected_mentees.csv, project_summary.csv,
                         mentee_project_summary.csv, debug_logs.csv
        """
        zip_buffer = io.BytesIO()
        log_buffer = io.StringIO()

        with zipfile.ZipFile(zip_buffer, 'w') as zf:
            projects = {entry.project for entry in queryset}
            log_buffer.write(f'Projects in selection: {len(projects)}\n')

            # Fetch all ranklist entries for these projects
            all_entries = (
                RankList.objects
                .filter(project__in=projects)
                .select_related('project', 'mentee__user')
            )
            log_buffer.write(f'Total RankList entries: {all_entries.count()}\n')

            project_data = {
                p.id: {
                    'project': p,
                    'max': int(p.mentee_max),
                    'ranked': {},   # mentee_id -> {rank, preference}
                    'selected': [],
                }
                for p in projects
            }

            # NEW: Because ranklist is per (project, mentee) there are no duplicates.
            # Each entry is already the single source of truth.
            for entry in all_entries:
                pid = entry.project.id
                mid = entry.mentee.id
                project_data[pid]['ranked'][mid] = {
                    'rank': entry.rank,
                    'preference': entry.preference,
                    'mentee': entry.mentee,
                }

            # Build sorted list per project
            for pid, pdata in project_data.items():
                sorted_mentees = sorted(
                    pdata['ranked'].items(),
                    key=lambda kv: (kv[1]['rank'], kv[1]['preference']),
                )
                pdata['sorted_mentees'] = sorted_mentees
                log_buffer.write(
                    f"Project '{pdata['project'].title}': "
                    f"{len(sorted_mentees)} ranked mentees, max={pdata['max']}\n"
                )

            # Assign by preference round
            assigned_mentees = set()
            all_mentee_ids = set()
            for pdata in project_data.values():
                all_mentee_ids.update(pdata['ranked'].keys())

            for pref_round in [1, 2, 3]:
                for pdata in project_data.values():
                    for mentee_id, info in pdata['sorted_mentees']:
                        if mentee_id in assigned_mentees:
                            continue
                        if info['preference'] != pref_round:
                            continue
                        if len(pdata['selected']) < pdata['max']:
                            pdata['selected'].append({
                                'mentee': info['mentee'],
                                'rank': info['rank'],
                                'preference': info['preference'],
                                'project': pdata['project'],
                            })
                            assigned_mentees.add(mentee_id)

            log_buffer.write(f'Total assigned: {len(assigned_mentees)}\n')
            log_buffer.write(f'Total unassigned: {len(all_mentee_ids - assigned_mentees)}\n')

            # --- CSV 1: selected_mentees.csv ---
            sel_buf = io.StringIO()
            sel_writer = csv.writer(sel_buf)
            sel_writer.writerow([
                'Domain', 'Project ID', 'Project Title',
                'Mentor Names', 'Mentor Rolls',
                'Mentee Roll', 'Mentee Name', 'Rank', 'Mentee Preference',
            ])
            for pdata in project_data.values():
                p = pdata['project']
                mentors = Mentor.objects.filter(projects=p).select_related('user')
                mentor_names = ', '.join(m.user.name for m in mentors) or '—'
                mentor_rolls = ', '.join(m.user.roll_number for m in mentors) or '—'
                domain = p.domain.slug if p.domain else ''
                for entry in pdata['selected']:
                    sel_writer.writerow([
                        domain, p.id, p.title,
                        mentor_names, mentor_rolls,
                        entry['mentee'].user.roll_number,
                        entry['mentee'].user.name,
                        entry['rank'], entry['preference'],
                    ])

            # Unassigned section
            sel_writer.writerow([])
            sel_writer.writerow(['--- Unassigned Mentees ---'])
            sel_writer.writerow(['Roll No', 'Name', 'Domain'])
            for mid in all_mentee_ids - assigned_mentees:
                m = next(
                    pdata['ranked'][mid]['mentee']
                    for pdata in project_data.values()
                    if mid in pdata['ranked']
                )
                domain = m.domain.slug if m.domain else ''
                sel_writer.writerow([m.user.roll_number, m.user.name, domain])

            zf.writestr('selected_mentees.csv', sel_buf.getvalue())

            # --- CSV 2: project_summary.csv ---
            sum_buf = io.StringIO()
            sum_writer = csv.writer(sum_buf)
            sum_writer.writerow(['Domain', 'Project ID', 'Project Title', 'Max', 'Selected', 'Remaining'])
            for pdata in project_data.values():
                p = pdata['project']
                sum_writer.writerow([
                    p.domain.slug if p.domain else '',
                    p.id, p.title, pdata['max'],
                    len(pdata['selected']),
                    pdata['max'] - len(pdata['selected']),
                ])
            zf.writestr('project_summary.csv', sum_buf.getvalue())

            # --- CSV 3: mentee_project_summary.csv ---
            mp_buf = io.StringIO()
            mp_writer = csv.writer(mp_buf)
            header = ['Roll No', 'Name', 'Domain']
            for i in range(1, 4):
                header.extend([f'Project {i}', f'Rank {i}', f'Pref {i}'])
            header.append('Final Assignment')
            mp_writer.writerow(header)

            # Build per-mentee view
            mentee_projects = defaultdict(list)
            for pdata in project_data.values():
                for mid, info in pdata['sorted_mentees']:
                    mentee_projects[mid].append(info)

            assigned_by_mentee = {
                entry['mentee'].id: pdata['project'].title
                for pdata in project_data.values()
                for entry in pdata['selected']
            }

            for mid, infos in mentee_projects.items():
                m = next(
                    pdata['ranked'][mid]['mentee']
                    for pdata in project_data.values()
                    if mid in pdata['ranked']
                )
                domain = m.domain.slug if m.domain else ''
                row = [m.user.roll_number, m.user.name, domain]
                for info in infos[:3]:
                    row.extend([info['mentee'].user.roll_number, info['rank'], info['preference']])
                while len(row) < 3 + 3 * 3:
                    row.extend(['', '', ''])
                row.append(assigned_by_mentee.get(mid, 'Not Assigned'))
                mp_writer.writerow(row)

            zf.writestr('mentee_project_summary.csv', mp_buf.getvalue())

            # --- CSV 4: debug_logs.csv ---
            log_csv = io.StringIO()
            log_writer = csv.writer(log_csv)
            log_writer.writerow(['Debug Log'])
            for line in log_buffer.getvalue().splitlines():
                log_writer.writerow([line])
            zf.writestr('debug_logs.csv', log_csv.getvalue())

        zip_buffer.seek(0)
        response = HttpResponse(zip_buffer, content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename="final_selection.zip"'
        return response
