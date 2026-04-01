from rest_framework.permissions import BasePermission

from .models import DomainMembership


def _get_user_memberships(user):
    """Return the queryset of approved memberships for the user."""
    return DomainMembership.objects.filter(user=user, is_approved=True)


def is_platform_manager(user):
    """True if user has a domain=None manager membership (platform-level manager)."""
    return _get_user_memberships(user).filter(role="manager", domain__isnull=True).exists()


def is_domain_manager(user, domain_slug):
    """True if user is a platform-level manager OR manager of the specific domain."""
    if is_platform_manager(user):
        return True
    return _get_user_memberships(user).filter(role="manager", domain__slug=domain_slug).exists()


def is_any_domain_manager(user):
    """True if user has any manager membership (platform or domain-level)."""
    return _get_user_memberships(user).filter(role="manager").exists()


class IsAnyDomainManager(BasePermission):
    """
    Grants access if the authenticated user is a manager in any domain
    (or the platform itself). Used to gate the manager dashboard.
    """
    message = "You must be a manager to access this resource."

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and is_any_domain_manager(request.user)


class IsDomainManager(BasePermission):
    """
    Grants access if the authenticated user is a manager of the domain
    whose slug appears in the URL kwargs as 'slug' or 'domain_slug'.
    Falls through to platform managers automatically.
    """
    message = "You must be a manager of this domain to perform this action."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        slug = view.kwargs.get("slug") or view.kwargs.get("domain_slug")
        if not slug:
            return False
        return is_domain_manager(request.user, slug)
