from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

class RollNumberBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, role=None):
        if not username or not password or not role:
            return None
        print(username,password,role)
        # Step 1: Filter by the provided role (mentee or mentor)
        try:
            users = get_user_model().objects.filter(username=username, role=role)
            if users.count() > 1:
                print(f"Multiple users found: {users}")
                for user in users:
                    print(f"Checking password for user: {user.username}")
                    if user.check_password(password):
                        return user  # Return the user whose password matches
                return None  # Return None if no password matches for any user
            elif users.count() == 1:
                user = users.first()
                print("hi",user)
                print(password,user.check_password(password))
                if user.check_password(password):
                    return user  # Return the user if password is correct
                print("bye")
                return None  # Return None if password doesn't match
            else:
                print("crazy")
                return None  # No user found with that username and role
        except ObjectDoesNotExist:
            return None  # No user found with that username and role
        
    
    def get_user(self, user_id):
        try:
            return get_user_model().objects.filter(pk=user_id).first()
        except ObjectDoesNotExist:
            return None
