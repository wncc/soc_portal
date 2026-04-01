"""
domains/admin.py  —  Admin for Domain and DomainMembership models
"""
import csv
from django.contrib import admin
from django.http import HttpResponse

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
        'created_at',
    )
    search_fields = ('slug', 'name')
    list_filter = ('is_active',)
    list_per_page = 100
    ordering = ('order', 'name')
    prepopulated_fields = {}  # slug is intentionally manual
    inlines = [DomainMembershipInline]
    actions = ['export_members_csv', 'activate_domains', 'deactivate_domains']

    readonly_fields = ('created_at',)

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
