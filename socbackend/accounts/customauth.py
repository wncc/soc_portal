from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist


class RollNumberBackend(BaseBackend):
    """
    Authenticates by username (roll number) + password only.
    Role is no longer part of authentication — it is determined by DomainMembership.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if not username or not password:
            return None

        try:
            user = get_user_model().objects.get(username=username)
            if user.check_password(password):
                return user
            return None
        except ObjectDoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return get_user_model().objects.filter(pk=user_id).first()
        except ObjectDoesNotExist:
            return None
