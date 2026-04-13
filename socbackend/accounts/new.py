from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
import logging
from .models import CustomUser, UserProfile

logger = logging.getLogger(__name__)

class CookieJWTAuthentication2(BaseAuthentication):
    def authenticate(self, request):
        print("\n" + "-"*80)
        print("[AUTH DEBUG] CookieJWTAuthentication2.authenticate called")
        print(f"[AUTH DEBUG] Request path: {request.path}")
        print(f"[AUTH DEBUG] Request method: {request.method}")
        
        # Try to get token from Authorization header
        token = request.headers.get("Authorization")
        print(f"[AUTH DEBUG] Authorization header: {token}")
        
        if not token:
            # Try to get from cookie
            cookie_token = request.COOKIES.get('auth')
            print(f"[AUTH DEBUG] Cookie 'auth': {cookie_token}")
            
            if not cookie_token:
                print("[AUTH DEBUG] No token found - returning None (unauthenticated)")
                print("-"*80 + "\n")
                # Return None instead of raising exception to allow unauthenticated access
                return None
            token = cookie_token
        
        # Remove "Bearer " from the token if it exists
        token = token.replace("Bearer ", "")
        print(f"[AUTH DEBUG] Cleaned token: {token[:30]}...")
        logger.debug(f"Received token: {token}")
        
        result = self.validate_custom_token(token)
        print(f"[AUTH DEBUG] Authentication result: {result}")
        print("-"*80 + "\n")
        return result

    def validate_custom_token(self, token):
        try:
            print(f"[AUTH DEBUG] Validating token: {token[:30]}...")
            
            # Check if the token is valid
            # You can validate the token here (check if it matches a known pattern, if it's expired, etc.)
            if not token or len(token) < 16:
                print(f"[AUTH DEBUG] Token validation failed: Invalid format (length: {len(token) if token else 0})")
                raise AuthenticationFailed("Invalid token format")

            # Validate the token (in this case, we check if it's a properly generated custom token)
            # In the absence of a database, you may have to use in-memory verification (or cache)
            if not self.is_token_valid(token):
                print(f"[AUTH DEBUG] Token validation failed: is_token_valid returned False")
                raise AuthenticationFailed("Invalid token")

            # Optionally, associate the token with a user
            user = self.get_user_from_token(token)
            if not user:
                print(f"[AUTH DEBUG] Token validation failed: No user found for token")
                raise AuthenticationFailed("No associated user for the token")
            
            print(f"[AUTH DEBUG] Token validation SUCCESS: User {user.username} (ID: {user.id})")
            # Return the user if valid
            return user, None

        except Exception as e:
            print(f"[AUTH DEBUG] Token validation EXCEPTION: {e}")
            logger.error(f"Error during token validation: {e}")
            raise AuthenticationFailed("Token validation failed")

    def is_token_valid(self, token):
        # Here you should implement the logic to validate the token format, expiration, etc.
        # For simplicity, let's assume we just check if the token is a valid length
        return True

    def get_user_from_token(self, token):
        try:
            print(f"[AUTH DEBUG] Extracting user from token: {token[:30]}...")
            
            # Token is structured as "<user_id>-<random>"
            user_id_str, _ = token.split('-', 1)
            user_id = int(user_id_str)
            print(f"[AUTH DEBUG] Extracted user_id: {user_id}")

            # Return the CustomUser directly — this is what AUTH_USER_MODEL is,
            # so request.user will always be a CustomUser instance.
            user = CustomUser.objects.get(pk=user_id)
            print(f"[AUTH DEBUG] Found user: {user.username} (ID: {user.id})")
            return user

        except Exception as e:
            print(f"[AUTH DEBUG] Error getting user from token: {e}")
            return None
