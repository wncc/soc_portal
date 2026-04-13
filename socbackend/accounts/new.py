from rest_framework.authentication import BaseAuthentication
import logging
from .models import CustomUser

logger = logging.getLogger(__name__)


class CookieJWTAuthentication2(BaseAuthentication):
    """
    Custom authentication that validates tokens from cookies or Authorization header.
    Checks the ActiveToken table to support server-side logout (token invalidation).
    Returns None for missing/invalid tokens (allows unauthenticated access).
    Views use @permission_classes([IsAuthenticated]) to require valid auth.
    """

    def authenticate(self, request):
        print("\n" + "-"*80)
        print("[AUTH DEBUG] CookieJWTAuthentication2.authenticate called")
        print(f"[AUTH DEBUG] Request path: {request.path}")

        # Prefer Authorization header, fall back to cookie
        token = request.headers.get("Authorization")
        if not token:
            token = request.COOKIES.get('auth')
            if not token:
                print("[AUTH DEBUG] No token found - unauthenticated")
                print("-"*80 + "\n")
                return None
        else:
            token = token.replace("Bearer ", "")

        token = token.replace("Bearer ", "")  # safe double-strip
        print(f"[AUTH DEBUG] Token (first 30): {token[:30]}...")

        result = self.validate_custom_token(token)
        print(f"[AUTH DEBUG] Result: {result}")
        print("-"*80 + "\n")
        return result

    def validate_custom_token(self, token):
        try:
            if not token or len(token) < 16 or '-' not in token:
                print("[AUTH DEBUG] Token format invalid")
                return None

            parts = token.split('-', 1)
            if len(parts) != 2:
                return None

            try:
                user_id = int(parts[0])
                if user_id <= 0:
                    return None
            except ValueError:
                return None

            # --- Server-side invalidation check ---
            # On logout, the ActiveToken row is deleted.
            # Even if the auth cookie persists in the browser, this check
            # rejects the token, effectively logging the user out.
            from .models import ActiveToken
            if not ActiveToken.objects.filter(token=token).exists():
                print(f"[AUTH DEBUG] Token not in ActiveToken table - logged out")
                return None

            user = self.get_user_from_token(token)
            if not user:
                return None

            print(f"[AUTH DEBUG] Auth SUCCESS: {user.username}")
            return user, None

        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return None

    def get_user_from_token(self, token):
        try:
            user_id = int(token.split('-', 1)[0])
            user = CustomUser.objects.get(pk=user_id)
            if not user.is_active:
                print(f"[AUTH DEBUG] User {user.username} inactive")
                return None
            return user
        except (ValueError, CustomUser.DoesNotExist, Exception) as e:
            print(f"[AUTH DEBUG] get_user error: {e}")
            return None
