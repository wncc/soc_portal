from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, UserProfile


# ---------------------------------------------------------------------------
# CustomUser Admin
# ---------------------------------------------------------------------------

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'is_active', 'is_staff', 'is_superuser', 'membership_summary')
    search_fields = ('username',)
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    ordering = ('username',)
    list_per_page = 500

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )

    def membership_summary(self, obj):
        from domains.models import DomainMembership
        memberships = DomainMembership.objects.filter(user=obj, is_approved=True).select_related('domain')
        if not memberships:
            return '—'
        parts = []
        for m in memberships:
            domain_label = m.domain.slug.upper() if m.domain else 'PLATFORM'
            parts.append(f'{domain_label}:{m.role}')
        return ' | '.join(parts)
    membership_summary.short_description = 'Domain Memberships'


# ---------------------------------------------------------------------------
# UserProfile Admin
# ---------------------------------------------------------------------------

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('roll_number', 'name', 'department', 'year', 'phone_number', 'verified')
    search_fields = ('roll_number', 'name', 'user__username')
    list_filter = ('department', 'year', 'verified')
    list_per_page = 500
    ordering = ('roll_number',)
