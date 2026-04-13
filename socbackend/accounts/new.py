from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
import logging
from .models import CustomUser, UserProfile

logger = logging.getLogger(__name__)

class CookieJWTAuthentication2(BaseAuthentication):
    """
    Custom authentication that validates tokens from cookies or Authorization header.
    Returns None for invalid tokens (allows unauthenticated access).
    Views can use @permission_classes([IsAuthenticated]) to require valid auth.
    """
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
                # Return None = no authentication provided (not an error)
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
            if not token or len(token) < 16:
                print(f"[AUTH DEBUG] Token validation failed: Invalid format (length: {len(token) if token else 0})")
                return None

            # Validate the token format (should be "<user_id>-<random>")
            if '-' not in token:
                print(f"[AUTH DEBUG] Token validation failed: Missing separator")
                return None
                
            parts = token.split('-', 1)
            if len(parts) != 2:
                print(f"[AUTH DEBUG] Token validation failed: Invalid format")
                return None
                
            try:
                user_id = int(parts[0])
                if user_id <= 0:
                    print(f"[AUTH DEBUG] Token validation failed: Invalid user_id")
                    return None
            except ValueError:
                print(f"[AUTH DEBUG] Token validation failed: user_id not a number")
                return None

            # Get user from token
            user = self.get_user_from_token(token)
            if not user:
                print(f"[AUTH DEBUG] Token validation failed: No user found for token")
                return None
            
            print(f"[AUTH DEBUG] Token validation SUCCESS: User {user.username} (ID: {user.id})")
            # Return the user if valid
            return user, None

        except Exception as e:
            print(f"[AUTH DEBUG] Token validation EXCEPTION: {e}")
            logger.error(f"Error during token validation: {e}")
            return None

    def get_user_from_token(self, token):
        try:
            print(f"[AUTH DEBUG] Extracting user from token: {token[:30]}...")
            
            # Token is structured as "<user_id>-<random>"
            user_id_str, _ = token.split('-', 1)
            user_id = int(user_id_str)
            print(f"[AUTH DEBUG] Extracted user_id: {user_id}")

            # Return the CustomUser directly
            user = CustomUser.objects.get(pk=user_id)
            
            # Check if user is active
            if not user.is_active:
                print(f"[AUTH DEBUG] User {user.username} is not active")
                return None
                
            print(f"[AUTH DEBUG] Found user: {user.username} (ID: {user.id})")
            return user

        except (ValueError, IndexError) as e:
            print(f"[AUTH DEBUG] Error parsing token: {e}")
            return None
        except CustomUser.DoesNotExist:
            print(f"[AUTH DEBUG] User not found in database")
            return None
        except Exception as e:
            print(f"[AUTH DEBUG] Unexpected error getting user from token: {e}")
            return None
