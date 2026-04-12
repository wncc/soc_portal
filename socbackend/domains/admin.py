"""
domains/admin.py  —  Admin for Domain and DomainMembership models
"""
import csv
from django import forms
from django.contrib import admin
from django.db import models
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import path
from django.contrib import messages

from .models import Domain, DomainMembership


# ===========================================================================
# Domain Admin
# ===========================================================================

class DomainMembershipInline(admin.TabularInline):
    model = DomainMembership
    extra = 0
    fields = ('user_display', 'role', 'is_approved', 'joined')
    readonly_fields = ('user_display', 'joined')
    can_delete = True
    show_change_link = True

    def user_display(self, obj):
        return f'{obj.user.username}'
    user_display.short_description = 'Roll No'


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = (
        'slug', 'name', 'is_active', 'order',
        'mentor_count', 'mentee_count', 'manager_count', 'pending_count',
        'created_at', 'bulk_import_link', 'allocation_link',
    )
    search_fields = ('slug', 'name')
    list_filter = ('is_active',)
    list_per_page = 100
    ordering = ('order', 'name')
    prepopulated_fields = {}  # slug is intentionally manual
    inlines = [DomainMembershipInline]
    actions = ['export_members_csv', 'activate_domains', 'deactivate_domains']

    readonly_fields = ('created_at',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:domain_id>/bulk-import/',
                self.admin_site.admin_view(self.bulk_import_view),
                name='domains_domain_bulk_import',
            ),
            path(
                '<int:domain_id>/allocate-projects/',
                self.admin_site.admin_view(self.allocate_projects_view),
                name='domains_domain_allocate',
            ),
        ]
        return custom_urls + urls

    fieldsets = (
        (None, {
            'fields': ('slug', 'name', 'description', 'cover_photo', 'is_active', 'order'),
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('memberships')

    def _count_role(self, obj, role, approved_only=True):
        qs = obj.memberships.filter(role=role)
        if approved_only:
            qs = qs.filter(is_approved=True)
        return qs.count()

    def mentor_count(self, obj):
        return self._count_role(obj, 'mentor')
    mentor_count.short_description = '✓ Mentors'

    def mentee_count(self, obj):
        return self._count_role(obj, 'mentee')
    mentee_count.short_description = '✓ Mentees'

    def manager_count(self, obj):
        return self._count_role(obj, 'manager')
    manager_count.short_description = '✓ Managers'

    def pending_count(self, obj):
        return obj.memberships.filter(is_approved=False).count()
    pending_count.short_description = '⏳ Pending'

    def bulk_import_link(self, obj):
        from django.urls import reverse
        from django.utils.html import format_html
        url = reverse('admin:domains_domain_bulk_import', args=[obj.pk])
        return format_html('<a class="button" href="{}">📋 Bulk Import</a>', url)
    bulk_import_link.short_description = 'Actions'
    
    def allocation_link(self, obj):
        from django.urls import reverse
        from django.utils.html import format_html
        url = reverse('admin:domains_domain_allocate', args=[obj.pk])
        return format_html('<a class="button" href="{}">🎯 Allocate Projects</a>', url)
    allocation_link.short_description = 'Allocation'

    @admin.action(description='Export all members of selected domains to CSV')
    def export_members_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="domain_members.csv"'
        writer = csv.writer(response)
        writer.writerow(['Domain', 'Domain Name', 'Roll No', 'Role', 'Approved', 'Joined'])
        for domain in queryset:
            for m in domain.memberships.select_related('user').all():
                writer.writerow([
                    domain.slug, domain.name, m.user.username,
                    m.role, 'Yes' if m.is_approved else 'No',
                    m.joined.strftime('%Y-%m-%d'),
                ])
        return response

    @admin.action(description='Activate selected domains')
    def activate_domains(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'Activated {updated} domain(s).')

    @admin.action(description='Deactivate selected domains')
    def deactivate_domains(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'Deactivated {updated} domain(s).')

    def bulk_import_view(self, request, domain_id):
        """Custom view for bulk importing projects into a domain."""
        from projects.bulk_import import parse_spreadsheet_data, bulk_import_projects as do_import
        
        domain = self.get_object(request, domain_id)
        if domain is None:
            self.message_user(request, 'Domain not found.', level=messages.ERROR)
            return redirect('admin:domains_domain_changelist')
        
        if request.method == 'POST':
            raw_data = ''
            
            # Check if file was uploaded
            if 'spreadsheet_file' in request.FILES:
                uploaded_file = request.FILES['spreadsheet_file']
                file_name = uploaded_file.name.lower()
                
                try:
                    # Handle Excel files
                    if file_name.endswith(('.xlsx', '.xls')):
                        try:
                            import openpyxl
                            import io
                            
                            # Read Excel file
                            workbook = openpyxl.load_workbook(io.BytesIO(uploaded_file.read()))
                            sheet = workbook.active
                            
                            # Convert to CSV format
                            rows = []
                            for row in sheet.iter_rows(values_only=True):
                                rows.append(','.join([str(cell) if cell is not None else '' for cell in row]))
                            raw_data = '\n'.join(rows)
                        except ImportError:
                            self.message_user(
                                request, 
                                'Excel support not installed. Please install openpyxl: pip install openpyxl',
                                level=messages.ERROR
                            )
                            raw_data = ''
                    else:
                        # Handle CSV/TSV files
                        raw_data = uploaded_file.read().decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        uploaded_file.seek(0)
                        raw_data = uploaded_file.read().decode('latin-1')
                    except Exception as e:
                        self.message_user(request, f'Error reading file: {str(e)}', level=messages.ERROR)
                        raw_data = ''
                except Exception as e:
                    self.message_user(request, f'Error processing file: {str(e)}', level=messages.ERROR)
                    raw_data = ''
            else:
                # Use pasted data
                raw_data = request.POST.get('spreadsheet_data', '')
            
            if not raw_data.strip():
                self.message_user(request, 'No data provided. Please upload a file or paste data.', level=messages.ERROR)
            else:
                try:
                    rows = parse_spreadsheet_data(raw_data)
                    if not rows:
                        self.message_user(request, 'No valid rows found in data.', level=messages.ERROR)
                    else:
                        success_count, errors = do_import(domain, rows, request)
                        
                        if success_count > 0:
                            self.message_user(
                                request,
                                f'✓ Successfully imported {success_count} project(s) into {domain.name}.',
                                level=messages.SUCCESS
                            )
                        
                        if errors:
                            for error in errors[:10]:
                                self.message_user(request, f'⚠ {error}', level=messages.WARNING)
                            if len(errors) > 10:
                                self.message_user(
                                    request,
                                    f'... and {len(errors) - 10} more errors.',
                                    level=messages.WARNING
                                )
                        
                        if not errors or success_count > 0:
                            return redirect('admin:domains_domain_changelist')
                        
                except Exception as e:
                    self.message_user(request, f'Import failed: {str(e)}', level=messages.ERROR)
        
        context = {
            **self.admin_site.each_context(request),
            'domain': domain,
            'opts': self.model._meta,
            'has_view_permission': self.has_view_permission(request),
            'title': f'Bulk Import Projects - {domain.name}',
        }
        return render(request, 'admin/domains/bulk_import_form.html', context)
    
    def allocate_projects_view(self, request, domain_id):
        """Generate project allocation for a domain using optimized algorithm."""
        from projects.models import Project, RankList, MenteePreference, Mentee, Mentor
        from collections import defaultdict, deque
        import heapq
        
        domain = self.get_object(request, domain_id)
        if domain is None:
            self.message_user(request, 'Domain not found.', level=messages.ERROR)
            return redirect('admin:domains_domain_changelist')
        
        # Get all projects for this domain
        projects = Project.objects.filter(domain=domain).prefetch_related('mentors')
        
        if not projects.exists():
            self.message_user(request, f'No projects found for {domain.name}.', level=messages.WARNING)
            return redirect('admin:domains_domain_changelist')
        
        # Build project data structure with O(1) lookup
        project_data = {}
        for p in projects:
            project_data[p.id] = {
                'project': p,
                'max': int(p.mentee_max),
                'ranked': {},
                'selected': [],
            }
        
        # Get all ranklists for these projects
        ranklists = RankList.objects.filter(project__in=projects).select_related('mentee__user', 'project')
        
        # If no ranklists exist, auto-create from preferences
        if not ranklists.exists():
            self.message_user(request, 'No ranklists found. Auto-creating from preferences...', level=messages.INFO)
            
            # Get all preferences for this domain
            preferences = MenteePreference.objects.filter(
                project__domain=domain
            ).select_related('mentee__user', 'project').order_by('project', 'preference')
            
            # Create ranklists based on preference order (batch create for efficiency)
            ranklist_to_create = []
            existing_ranks = {}
            
            for pref in preferences:
                key = (pref.project.id, pref.mentee.id)
                if key not in existing_ranks:
                    # Get current max rank for this project
                    if pref.project.id not in existing_ranks:
                        existing_ranks[pref.project.id] = 0
                    
                    existing_ranks[pref.project.id] += 1
                    ranklist_to_create.append(
                        RankList(
                            project=pref.project,
                            mentee=pref.mentee,
                            rank=existing_ranks[pref.project.id],
                            preference=pref.preference
                        )
                    )
            
            # Bulk create for efficiency
            if ranklist_to_create:
                RankList.objects.bulk_create(ranklist_to_create, ignore_conflicts=True)
            
            # Reload ranklists
            ranklists = RankList.objects.filter(project__in=projects).select_related('mentee__user', 'project')
            self.message_user(request, f'Created {ranklists.count()} ranklist entries.', level=messages.SUCCESS)
        
        # Populate ranked mentees using hash map for O(1) access
        for entry in ranklists:
            pid = entry.project.id
            mid = entry.mentee.id
            project_data[pid]['ranked'][mid] = {
                'rank': entry.rank,
                'preference': entry.preference,
                'mentee': entry.mentee,
            }
        
        # OPTIMIZED ALLOCATION ALGORITHM
        # Uses priority queue (heap) for efficient selection
        # Time complexity: O(M * log(M)) where M is number of mentees
        
        assigned_mentees = set()
        all_mentee_ids = set()
        
        # Build mentee -> projects mapping for quick lookup
        mentee_preferences = defaultdict(list)
        for pid, pdata in project_data.items():
            all_mentee_ids.update(pdata['ranked'].keys())
            for mid, info in pdata['ranked'].items():
                mentee_preferences[mid].append((info['preference'], info['rank'], pid, info))
        
        # Sort each mentee's preferences once
        for mid in mentee_preferences:
            mentee_preferences[mid].sort()  # Sort by (preference, rank)
        
        # Allocate by preference rounds using priority queue
        for pref_round in [1, 2, 3]:
            # Build priority queue: (rank, mentee_id, project_id)
            pq = []
            
            for mid in all_mentee_ids:
                if mid in assigned_mentees:
                    continue
                
                # Find this mentee's choice for current preference round
                for pref, rank, pid, info in mentee_preferences[mid]:
                    if pref == pref_round:
                        heapq.heappush(pq, (rank, mid, pid, info))
                        break
            
            # Process queue: assign mentees in rank order
            while pq:
                rank, mid, pid, info = heapq.heappop(pq)
                
                if mid in assigned_mentees:
                    continue
                
                pdata = project_data[pid]
                if len(pdata['selected']) < pdata['max']:
                    pdata['selected'].append({
                        'mentee': info['mentee'],
                        'rank': rank,
                        'preference': pref_round,
                        'project': pdata['project'],
                    })
                    assigned_mentees.add(mid)
        
        # Generate CSV
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{domain.slug}_allocation.csv"'
        writer = csv.writer(response)
        
        # Header
        writer.writerow([
            'Domain', 'Project ID', 'Project Title',
            'Mentor Names', 'Mentor Rolls', 'Mentor Phones',
            'Mentee Roll', 'Mentee Name', 'Mentee Phone',
            'Rank', 'Mentee Preference', 'Max Mentees', 'Selected Count'
        ])
        
        # Write allocations
        for pdata in project_data.values():
            p = pdata['project']
            mentors = Mentor.objects.filter(projects=p).select_related('user')
            mentor_names = ', '.join(m.user.name for m in mentors) or '—'
            mentor_rolls = ', '.join(m.user.roll_number for m in mentors) or '—'
            mentor_phones = ', '.join(m.user.phone_number for m in mentors) or '—'
            
            for entry in pdata['selected']:
                writer.writerow([
                    domain.slug.upper(),
                    p.id,
                    p.title,
                    mentor_names,
                    mentor_rolls,
                    mentor_phones,
                    entry['mentee'].user.roll_number,
                    entry['mentee'].user.name,
                    entry['mentee'].user.phone_number,
                    entry['rank'],
                    entry['preference'],
                    pdata['max'],
                    len(pdata['selected']),
                ])
        
        # Summary section
        writer.writerow([])
        writer.writerow(['--- SUMMARY ---'])
        writer.writerow(['Total Projects', len(project_data)])
        writer.writerow(['Total Mentees Applied', len(all_mentee_ids)])
        writer.writerow(['Total Mentees Assigned', len(assigned_mentees)])
        writer.writerow(['Total Mentees Unassigned', len(all_mentee_ids - assigned_mentees)])
        
        # Unassigned mentees
        writer.writerow([])
        writer.writerow(['--- UNASSIGNED MENTEES ---'])
        writer.writerow(['Roll No', 'Name', 'Phone'])
        for mid in all_mentee_ids - assigned_mentees:
            m = next(
                pdata['ranked'][mid]['mentee']
                for pdata in project_data.values()
                if mid in pdata['ranked']
            )
            writer.writerow([m.user.roll_number, m.user.name, m.user.phone_number])
        
        # Project summary
        writer.writerow([])
        writer.writerow(['--- PROJECT SUMMARY ---'])
        writer.writerow(['Project ID', 'Project Title', 'Max', 'Selected', 'Remaining'])
        for pdata in project_data.values():
            p = pdata['project']
            writer.writerow([
                p.id,
                p.title,
                pdata['max'],
                len(pdata['selected']),
                pdata['max'] - len(pdata['selected']),
            ])
        
        self.message_user(
            request,
            f'Generated allocation for {domain.name}: {len(assigned_mentees)} mentees assigned.',
            level=messages.SUCCESS
        )
        
        return response


# ===========================================================================
# DomainMembership Admin
# ===========================================================================

@admin.register(DomainMembership)
class DomainMembershipAdmin(admin.ModelAdmin):
    list_display = (
        'roll_number', 'domain_display', 'role', 'is_approved', 'joined',
    )
    search_fields = ('user__username',)
    list_filter = ('role', 'is_approved', 'domain')
    list_per_page = 1000
    ordering = ('-joined',)
    actions = ['approve_memberships', 'revoke_memberships', 'export_memberships_csv']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'domain')

    def roll_number(self, obj):
        return obj.user.username
    roll_number.short_description = 'Roll No'
    roll_number.admin_order_field = 'user__username'

    def domain_display(self, obj):
        if obj.domain is None:
            return '🌐 PLATFORM (all domains)'
        return f'{obj.domain.slug.upper()} — {obj.domain.name}'
    domain_display.short_description = 'Domain'
    domain_display.admin_order_field = 'domain__slug'

    @admin.action(description='Approve selected memberships')
    def approve_memberships(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'Approved {updated} membership(s).')

    @admin.action(description='Revoke (unapprove) selected memberships')
    def revoke_memberships(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'Revoked {updated} membership(s).')

    @admin.action(description='Export selected memberships to CSV')
    def export_memberships_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="memberships.csv"'
        writer = csv.writer(response)
        writer.writerow(['Roll No', 'Domain Slug', 'Domain Name', 'Role', 'Approved', 'Joined'])
        for m in queryset.select_related('user', 'domain'):
            writer.writerow([
                m.user.username,
                m.domain.slug if m.domain else 'PLATFORM',
                m.domain.name if m.domain else 'All Domains',
                m.role,
                'Yes' if m.is_approved else 'No',
                m.joined.strftime('%Y-%m-%d'),
            ])
        return response
