from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
import logging
from .models import CustomUser, UserProfile

logger = logging.getLogger(__name__)

class CookieJWTAuthentication2(BaseAuthentication):
    def authenticate(self, request):
        # Try to get token from Authorization header
        token = request.headers.get("Authorization")
        
        if not token:
            # Return None instead of raising exception to allow unauthenticated access
            return None
        
        # Remove "Bearer " from the token if it exists
        token = token.replace("Bearer ", "")
        logger.debug(f"Received token: {token}")
        
        return self.validate_custom_token(token)

    def validate_custom_token(self, token):
        try:
            # Check if the token is valid
            # You can validate the token here (check if it matches a known pattern, if it's expired, etc.)
            if not token or len(token) < 16:
                raise AuthenticationFailed("Invalid token format")

            # Validate the token (in this case, we check if it's a properly generated custom token)
            # In the absence of a database, you may have to use in-memory verification (or cache)
            if not self.is_token_valid(token):
                raise AuthenticationFailed("Invalid token")

            # Optionally, associate the token with a user
            user = self.get_user_from_token(token)
            if not user:
                raise AuthenticationFailed("No associated user for the token")
            
            # Return the user if valid
            return user, None

        except Exception as e:
            logger.error(f"Error during token validation: {e}")
            raise AuthenticationFailed("Token validation failed")

    def is_token_valid(self, token):
        # Here you should implement the logic to validate the token format, expiration, etc.
        # For simplicity, let's assume we just check if the token is a valid length
        return True

    def get_user_from_token(self, token):
        try:
            # Token is structured as "<user_id>-<random>"
            user_id_str, _ = token.split('-', 1)
            user_id = int(user_id_str)

            # Return the CustomUser directly — this is what AUTH_USER_MODEL is,
            # so request.user will always be a CustomUser instance.
            user = CustomUser.objects.get(pk=user_id)
            return user

        except Exception as e:
            print(f"Error getting user from token: {e}")
            return None
