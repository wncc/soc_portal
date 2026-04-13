import re
import os
import secrets

from django.http import JsonResponse
from django.db.models import Value as V, Q
from django.db.models.functions import Concat
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.exceptions import APIException, AuthenticationFailed
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.db import models

import requests

from socbackend.settings import SIMPLE_JWT
from django.core.mail import send_mail
from django.conf import settings
from django.utils.crypto import get_random_string

from .helpers import fetch_from_sso
from .models import UserProfile, CustomUser
from .serializers import RegisterUserSerializer, UserAutoCompleteSerializer, UserProfileSerializer
from .options import DepartmentChoices, YearChoices
from .customauth import RollNumberBackend
from .new import CookieJWTAuthentication2


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_memberships_response(user):
    """
    Build the memberships array for token responses.
    Returns (memberships_list, is_manager).
    """
    from domains.models import DomainMembership
    from domains.serializers import MyMembershipSerializer

    memberships = DomainMembership.objects.filter(user=user, is_approved=True).select_related("domain")
    data = MyMembershipSerializer(memberships, many=True).data
    is_manager = any(m["role"] == "manager" for m in data)
    return data, is_manager


def _auto_link_mentor_projects(user):
    """
    Auto-link projects to mentor on first login.
    Searches for projects where mentor field contains this user's roll number.
    Also creates DomainMembership and Mentor objects automatically.
    """
    try:
        from projects.models import Project, Mentor
        from domains.models import DomainMembership
        
        profile = UserProfile.objects.get(user=user)
        roll = profile.roll_number.lower()
        
        # Find projects where this user is mentioned as mentor or co-mentor
        import re
        
        # Search in mentor field
        projects_as_mentor = Project.objects.filter(
            models.Q(mentor__icontains=roll) | 
            models.Q(co_mentor_info__icontains=roll)
        ).select_related('domain')
        
        linked_count = 0
        for project in projects_as_mentor:
            # Verify roll number match (exact match in parentheses or standalone)
            mentor_match = re.search(rf'\b{re.escape(roll)}\b', project.mentor.lower())
            co_mentor_match = re.search(rf'\b{re.escape(roll)}\b', project.co_mentor_info.lower())
            
            if mentor_match or co_mentor_match:
                # Create DomainMembership automatically (no need to apply!)
                membership, _ = DomainMembership.objects.get_or_create(
                    user=user,
                    domain=project.domain,
                    role='mentor',
                    defaults={'is_approved': True}
                )
                
                # Get or create Mentor object for this domain
                mentor_obj, created = Mentor.objects.get_or_create(
                    user=profile,
                    domain=project.domain,
                    defaults={'season': '1'}
                )
                
                # Link project if not already linked
                if project not in mentor_obj.projects.all():
                    mentor_obj.projects.add(project)
                    linked_count += 1
        
        if linked_count > 0:
            print(f"[AUTO-LINK] Linked {linked_count} projects to {roll} (DomainMembership + Mentor created)")
        
        return linked_count
    except Exception as e:
        print(f"[AUTO-LINK ERROR] {str(e)}")
        return 0


# ---------------------------------------------------------------------------
# Utility Views
# ---------------------------------------------------------------------------

class DepartmentListAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(DepartmentChoices.choices)


class YearListAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(YearChoices.choices)


@api_view(["POST"])
@authentication_classes([])
@permission_classes([AllowAny])
def get_sso_user_data(request):
    print("\n" + "="*80)
    print("[SSO DEBUG] get_sso_user_data called")
    print(f"[SSO DEBUG] Request method: {request.method}")
    print(f"[SSO DEBUG] Request headers: {dict(request.headers)}")
    print(f"[SSO DEBUG] Request data: {request.data}")
    print(f"[SSO DEBUG] Request user: {request.user}")
    print(f"[SSO DEBUG] Is authenticated: {request.user.is_authenticated if hasattr(request.user, 'is_authenticated') else 'N/A'}")
    
    accessid = request.data.get("accessid")
    print(f"[SSO DEBUG] Extracted accessid: {accessid}")
    
    if not accessid:
        print("[SSO DEBUG] ERROR: Missing accessid")
        return Response({"error": "Missing accessid"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        print(f"[SSO DEBUG] Fetching user data for accessid: {accessid[:20]}...")
        print(f"[SSO DEBUG] Calling: http://sso.tech-iitb.org/project/getuserdata")
        
        response = requests.post(
            "http://sso.tech-iitb.org/project/getuserdata",
            json={"id": accessid},
        )
        
        print(f"[SSO DEBUG] SSO response status: {response.status_code}")
        print(f"[SSO DEBUG] SSO response text: {response.text}")
        
        data = response.json()
        print(f"[SSO DEBUG] SSO response JSON: {data}")

        if response.status_code == 200:
            print(f"[SSO DEBUG] SUCCESS: Returning user data")
            print("="*80 + "\n")
            return Response(data, status=status.HTTP_200_OK)
        else:
            print(f"[SSO DEBUG] ERROR: SSO returned status {response.status_code}")
            print("="*80 + "\n")
            return Response({"error": "Failed to fetch user data"}, status=response.status_code)

    except Exception as e:
        print(f"[SSO DEBUG] EXCEPTION: {str(e)}")
        import traceback
        print(f"[SSO DEBUG] Traceback: {traceback.format_exc()}")
        print("="*80 + "\n")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from .new import CookieJWTAuthentication2

@api_view(["GET"])
@authentication_classes([CookieJWTAuthentication2])
@permission_classes([AllowAny])
def isloggedin(request):
    print("\n" + "="*80)
    print("[ISLOGGEDIN DEBUG] Checking login status")
    print(f"[ISLOGGEDIN DEBUG] User: {request.user}")
    print(f"[ISLOGGEDIN DEBUG] Is authenticated: {request.user.is_authenticated if hasattr(request.user, 'is_authenticated') else False}")
    
    # Check if a token was provided (in cookie or header)
    has_token = bool(request.COOKIES.get('auth') or request.headers.get('Authorization'))
    print(f"[ISLOGGEDIN DEBUG] Has token: {has_token}")
    
    if request.user and request.user.is_authenticated:
        print(f"[ISLOGGEDIN DEBUG] User IS logged in: {request.user.username}")
        print("="*80 + "\n")
        return JsonResponse({"status": "YES"}, status=200)
    else:
        print("[ISLOGGEDIN DEBUG] User NOT logged in")
        
        # If token was provided but authentication failed, return 401 and clear cookie
        if has_token:
            print("[ISLOGGEDIN DEBUG] Invalid token detected - returning 401")
            print("="*80 + "\n")
            response = JsonResponse({"status": "NO", "error": "Invalid or expired token"}, status=401)
            if request.COOKIES.get('auth'):
                print("[ISLOGGEDIN DEBUG] Clearing invalid auth cookie")
                response.delete_cookie('auth')
            return response
        else:
            # No token provided - user is simply not logged in (not an error)
            print("[ISLOGGEDIN DEBUG] No token provided - returning 200")
            print("="*80 + "\n")
            return JsonResponse({"status": "NO"}, status=200)


def generate_verification_token():
    return get_random_string(length=32)


def verify_email(request, token):
    try:
        user_profile = UserProfile.objects.get(verification_token=token)
        user_profile.verified = True
        user = user_profile.user
        user.is_active = True
        user.save()
        user_profile.save()
        return JsonResponse({"success": "verified"}, status=200)
    except UserProfile.DoesNotExist:
        return JsonResponse({"error": "User does not exist"}, status=400)


def send_verification_email(user_profile):
    subject = "SOC Mentee Registration Verification Link"
    message = f"""
    Hi {user_profile.name},

    Please click on the link below to verify your email address and complete your registration.

    http://localhost:3000/wncc-soc/verify-email/{user_profile.verification_token}

    Regards,
    Team WnCC
    """
    from_email = os.getenv("EMAIL_HOST_USER")
    recipient_list = [f"{user_profile.roll_number}@iitb.ac.in"]
    print(f"Sending email from: {from_email} to: {recipient_list}")
    send_mail(subject, message, from_email, recipient_list, auth_password="xjsgrdmwcgdvqypt")


@api_view(["GET"])
@permission_classes([AllowAny])
def logout(request):
    print("\n" + "="*80)
    print("[LOGOUT DEBUG] Logout endpoint called")
    
    response = JsonResponse({"success": "logged out"}, status=200)
    
    # 'auth' cookie was set without an explicit domain, so delete it the same way.
    # Trying multiple domain variants ensures we catch cookies set by different
    # parts of the stack (Django session middleware, etc.).
    cookie_names = [SIMPLE_JWT["AUTH_COOKIE"], 'sessionid', 'csrftoken']
    
    for cookie_name in cookie_names:
        # Delete without domain (matches cookies set against the exact host)
        response.delete_cookie(cookie_name, path='/')
        # Delete with parent-domain variants (catches cookies scoped to .tech-iitb.org)
        response.delete_cookie(cookie_name, path='/', domain='.tech-iitb.org')
        response.delete_cookie(cookie_name, path='/', domain='socb.tech-iitb.org')
        response.delete_cookie(cookie_name, path='/', domain='.socb.tech-iitb.org')
    
    # Also invalidate Django's server-side session if one exists
    if hasattr(request, 'session'):
        request.session.flush()
    
    print("[LOGOUT DEBUG] All cookies cleared and session flushed")
    print("="*80 + "\n")
    
    return response


# ---------------------------------------------------------------------------
# Registration Views
# ---------------------------------------------------------------------------

class RegisterUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        roll_number = request.data.get("roll_number", "").lower()
        password = request.data.get("password")

        if CustomUser.objects.filter(username=roll_number).exists():
            user = CustomUser.objects.get(username=roll_number)
            if UserProfile.objects.filter(user=user).exists():
                user_profile = UserProfile.objects.get(user=user)
                if user_profile.verified:
                    return Response({"error": "User already exists"}, status=400)
                else:
                    user.delete()
            else:
                user.delete()

        user = CustomUser.objects.create_user(username=roll_number, password=password)
        user.is_active = False
        user.save()

        mutable_copy = request.POST.copy()
        mutable_copy["user"] = user.id
        serializer = RegisterUserSerializer(data=mutable_copy)

        if serializer.is_valid():
            serializer.save()
            verification_token = generate_verification_token()
            user_profile = UserProfile.objects.get(user=user)
            user_profile.verification_token = verification_token
            user_profile.verified = False
            user.is_active = False
            user.save()
            user_profile.save()
            send_verification_email(user_profile)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class RegisterUserViewSSO(APIView):
    """
    SSO registration — creates a single CustomUser per roll number (no role).
    Domain-specific roles are added later via DomainMembership.
    """
    authentication_classes = []  # Disable authentication for registration
    permission_classes = [AllowAny]

    def post(self, request):
        print("\n" + "="*80)
        print("[SSO REGISTER DEBUG] RegisterUserViewSSO called")
        print(f"[SSO REGISTER DEBUG] Request data: {request.data}")
        
        roll_number = request.data.get("roll_number", "").lower()
        password = request.data.get("password")
        print(f"[SSO REGISTER DEBUG] Roll number: {roll_number}")

        # If user already exists and is verified, return error
        if CustomUser.objects.filter(username=roll_number).exists():
            print(f"[SSO REGISTER DEBUG] User {roll_number} already exists")
            user = CustomUser.objects.get(username=roll_number)
            if UserProfile.objects.filter(user=user).exists():
                user_profile = UserProfile.objects.get(user=user)
                if user_profile.verified:
                    print(f"[SSO REGISTER DEBUG] ERROR: User {roll_number} already verified")
                    return Response({"error": "User already exists"}, status=400)
                else:
                    print(f"[SSO REGISTER DEBUG] Deleting unverified user {roll_number}")
                    user.delete()
            else:
                print(f"[SSO REGISTER DEBUG] Deleting user {roll_number} without profile")
                user.delete()

        print(f"[SSO REGISTER DEBUG] Creating new user {roll_number}")
        user = CustomUser.objects.create_user(username=roll_number, password=password)
        user.is_active = True
        user.save()
        print(f"[SSO REGISTER DEBUG] User created: {user.username} (ID: {user.id})")

        mutable_copy = request.POST.copy()
        mutable_copy["user"] = user.id
        serializer = RegisterUserSerializer(data=mutable_copy)

        if serializer.is_valid():
            print(f"[SSO REGISTER DEBUG] Serializer valid, saving profile")
            serializer.save()
            user_profile = UserProfile.objects.get(user=user)
            user_profile.verified = True
            user.is_active = True
            user.save()
            user_profile.save()
            print(f"[SSO REGISTER DEBUG] Profile saved and verified")

            memberships, is_manager = _build_memberships_response(user)
            print(f"[SSO REGISTER DEBUG] SUCCESS: User registered with {len(memberships)} memberships")
            print("="*80 + "\n")
            return Response(
                {**serializer.data, "memberships": memberships, "is_manager": is_manager},
                status=201,
            )
        
        print(f"[SSO REGISTER DEBUG] ERROR: Serializer errors: {serializer.errors}")
        print("="*80 + "\n")
        return Response(serializer.errors, status=400)


# ---------------------------------------------------------------------------
# Auth Token Views
# ---------------------------------------------------------------------------

class CustomTokenObtainPairView(TokenObtainPairView):
    """Legacy password-based login (still works, now role-free)."""

    def post(self, request, *args, **kwargs):
        mutable_copy = request.POST.copy()
        username = mutable_copy.get("username", "").lower()
        password = request.data.get("password")

        backend = RollNumberBackend()
        user = backend.authenticate(request=request, username=username, password=password)

        if user is None:
            raise AuthenticationFailed("Invalid roll number or password")
        
        # Update last_login timestamp
        from django.utils import timezone
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        # Auto-link projects on login
        _auto_link_mentor_projects(user)

        random_token = secrets.token_urlsafe(16)
        custom_token = f"{user.id}-{random_token}"

        memberships, is_manager = _build_memberships_response(user)

        response_data = {
            "access": custom_token,
            "memberships": memberships,
            "is_manager": is_manager,
        }
        response = JsonResponse(response_data)
        response.set_cookie(key="auth", value=custom_token, httponly=True)
        print(f"Cookie set with value: {custom_token} | last_login updated")
        return response


class CustomSSOTokenView(APIView):
    """
    SSO token endpoint. No longer requires role parameter — looks up user by username only.
    Returns memberships array for the frontend to determine where to redirect.
    """
    authentication_classes = []  # Disable authentication for token generation
    permission_classes = [AllowAny]

    def post(self, request):
        print("\n" + "="*80)
        print("[SSO TOKEN DEBUG] CustomSSOTokenView called")
        print(f"[SSO TOKEN DEBUG] Request data: {request.data}")
        
        roll_number = request.data.get("username", "").lower()
        print(f"[SSO TOKEN DEBUG] Roll number: {roll_number}")

        if not roll_number:
            print("[SSO TOKEN DEBUG] ERROR: Roll number missing")
            raise AuthenticationFailed("Roll number is required")

        try:
            user = CustomUser.objects.get(username=roll_number)
            print(f"[SSO TOKEN DEBUG] User found: {user.username} (ID: {user.id})")
        except CustomUser.DoesNotExist:
            print(f"[SSO TOKEN DEBUG] ERROR: User {roll_number} does not exist")
            raise AuthenticationFailed("User does not exist. Please register first.")

        if not user.is_active:
            print(f"[SSO TOKEN DEBUG] ERROR: User {roll_number} is not active")
            raise AuthenticationFailed("User is not active")
        
        # Update last_login timestamp (Django's built-in field)
        from django.utils import timezone
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        print(f"[SSO TOKEN DEBUG] Updated last_login for {user.username}")
        
        # Auto-link projects on login
        linked = _auto_link_mentor_projects(user)
        print(f"[SSO TOKEN DEBUG] Auto-linked {linked} projects")

        random_token = secrets.token_urlsafe(16)
        custom_token = f"{user.id}-{random_token}"
        print(f"[SSO TOKEN DEBUG] Generated token: {custom_token}")

        memberships, is_manager = _build_memberships_response(user)
        print(f"[SSO TOKEN DEBUG] Memberships: {len(memberships)}, is_manager: {is_manager}")

        response_data = {
            "access": custom_token,
            "memberships": memberships,
            "is_manager": is_manager,
        }

        response = JsonResponse(response_data)
        response.set_cookie(key="auth", value=custom_token, httponly=True)
        print(f"[SSO TOKEN DEBUG] SUCCESS: Token issued and cookie set")
        print("="*80 + "\n")
        return response


# ---------------------------------------------------------------------------
# Manager Bootstrap View
# ---------------------------------------------------------------------------

class BecomeManagerView(APIView):
    """
    GET /api/accounts/become-manager/<secret>/

    A secret URL sent to ITC managers. When visited while logged in via SSO,
    grants the user a platform-level manager DomainMembership (domain=None).
    This gives them access to the manager dashboard for ALL domains.

    Set the secret token in .env:  MANAGER_SECRET_TOKEN=<your-secret>
    """
    authentication_classes = [CookieJWTAuthentication2]
    permission_classes = [IsAuthenticated]

    def get(self, request, secret):
        expected = getattr(settings, "MANAGER_SECRET_TOKEN", "")

        if not expected or secret != expected:
            return Response(
                {"error": "Invalid or expired manager token."},
                status=status.HTTP_403_FORBIDDEN,
            )

        from domains.models import DomainMembership

        membership, created = DomainMembership.objects.get_or_create(
            user=request.user,
            domain=None,   # Platform-level: manages all domains
            role="manager",
            defaults={"is_approved": True},
        )

        if created:
            return Response({
                "success": True,
                "message": f"You are now a platform manager. Welcome to Summer of Tech! "
                           f"Visit /manager to access your dashboard.",
                "is_manager": True,
            })
        else:
            return Response({
                "success": True,
                "message": "You are already a platform manager.",
                "is_manager": True,
            })


# ---------------------------------------------------------------------------
# Profile & Membership Views
# ---------------------------------------------------------------------------

class UserProfileView(APIView):
    authentication_classes = [CookieJWTAuthentication2]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_profile = UserProfile.objects.get(user=request.user)
        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data)

    def post(self, request):
        user_profile = UserProfile.objects.get(user=request.user)
        serializer = UserProfileSerializer(user_profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    
    def patch(self, request):
        """Update phone number specifically"""
        user_profile = UserProfile.objects.get(user=request.user)
        phone = request.data.get('phone_number')
        if phone:
            user_profile.phone_number = phone
            user_profile.save()
            return Response({"success": True, "phone_number": phone})
        return Response({"error": "Phone number required"}, status=400)


class MyMembershipsView(APIView):
    """
    GET /api/accounts/my-memberships/
    Returns all approved domain+role pairs for the logged-in user.
    """
    authentication_classes = [CookieJWTAuthentication2]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        memberships, is_manager = _build_memberships_response(request.user)
        
        # Check if phone number is missing or invalid
        try:
            profile = UserProfile.objects.get(user=request.user)
            phone = profile.phone_number or ""
            # Consider empty, whitespace-only, or all zeros as needing update
            needs_phone = (
                not phone.strip() or 
                phone.strip() == "0000000000" or
                len(phone.strip()) < 10
            )
        except UserProfile.DoesNotExist:
            needs_phone = True
        
        return Response({
            "memberships": memberships,
            "is_manager": is_manager,
            "needs_phone_update": needs_phone,
        })


class UserAutoCompleteView(ListAPIView):
    """ListAPIView to access user data, for user searching."""
    serializer_class = UserAutoCompleteSerializer

    def get_queryset(self):
        queryset = UserProfile.objects.all()
        query = self.request.query_params.get("search")

        if query is not None and query != "":
            if re.search(r"\d", query):
                queryset = queryset.filter(user__roll_number__iexact=query)
            else:
                queryset = queryset.annotate(
                    full_name=Concat("user__first_name", V(" "), "user__last_name")
                )
                for term in query.split():
                    queryset = queryset.filter(full_name__icontains=term)

        return queryset[:10]


class CreateUserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = fetch_from_sso(request.data["code"], "http://localhost:3000/register", request)
        except APIException as e:
            return Response(e.detail, status=e.status_code)
        return Response(data)
