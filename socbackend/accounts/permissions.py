from rest_framework.permissions import BasePermission
from django.core.exceptions import ObjectDoesNotExist


class HasUserProfile(BasePermission):
    message = "User must have created their profile."

    def has_permission(self, request, view):
        # Allow unauthenticated requests to pass through
        if not request.user or not request.user.is_authenticated:
            return True
        
        try:
            request.user.userprofile  # Will raise an error if the user does not have a profile
            return True
        except ObjectDoesNotExist:
            return False
