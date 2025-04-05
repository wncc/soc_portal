import re
from django.http import JsonResponse
from django.db.models import Value as V
from django.db.models.functions import Concat
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.exceptions import APIException

from socbackend.settings import SIMPLE_JWT
from django.core.mail import send_mail

from .helpers import fetch_from_sso
from .models import UserProfile
from django.contrib.auth.models import User
from .serializers import RegisterUserSerializer, UserAutoCompleteSerializer, UserProfileSerializer

from projects.models import Mentee
from projects.models import Mentor

from .options import DepartmentChoices, YearChoices
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import CustomUser


from django.utils.crypto import get_random_string
import os


# views.py
from rest_framework import generics
from rest_framework.response import Response
from .models import DepartmentChoices

class DepartmentListAPIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        departments = DepartmentChoices.choices
        return Response(departments)
    

class YearListAPIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        years = YearChoices.choices
        return Response(years)
 
 
import requests
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
   
@api_view(['POST'])
@permission_classes([AllowAny])
def get_sso_user_data(request):
    accessid = request.data.get('accessid')
    if not accessid:
        return Response({"error": "Missing accessid"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        print(accessid)
        response = requests.post(
            "http://sso.tech-iitb.org/project/getuserdata",
            json={"id": accessid}
        )
        print("Raw SSO response text:", response.text)  # helpful for debugging

        data = response.json()

        if response.status_code == 200:
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Failed to fetch user data"}, status=response.status_code)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def isloggedin(request):
    if isinstance(request.user, CustomUser):
        return JsonResponse({"status": "NO"}, status=200)
    else:
        return JsonResponse({"status": "YES"}, status=200)

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
        mentee = Mentee.objects.create(user=user_profile)
        mentee.save()


        return JsonResponse({"success": "verified"}, status=200)
    except UserProfile.DoesNotExist:
        return JsonResponse({"error": "User does not exist"}, status=400)

def send_verification_email(user_profile):
    subject = 'SOC Menteee Registration Verification Link'
    message = f"""
    Hi {user_profile.name},
    
    Please click on the link below to verify your email address and complete your registration.
    
    http://localhost:3000/wncc-soc/verify-email/{user_profile.verification_token}
    
    Regards,
    Team WnCC
    """

    from_email = os.getenv("EMAIL_HOST_USER")  # Use the configured sender email
    recipient_list = [f"{user_profile.roll_number}@iitb.ac.in"]  # IITB email
    #recipient_list = ["23b2401@iitb.ac.in"]

    print(f"Sending email from: {from_email} to: {recipient_list}")

    print(from_email,recipient_list,user_profile.verification_token)
    send_mail(subject, message, from_email, recipient_list,auth_password="xjsgrdmwcgdvqypt")  
    

def logout(request):
    response = JsonResponse({"success": "logged out"}, status=200)
    response.delete_cookie(SIMPLE_JWT["AUTH_COOKIE"])
    return response


class RegisterUserView(APIView):
    permission_classes = [AllowAny]  

    def post(self, request):
        roll_number = request.data.get("roll_number").lower()
        password = request.data.get("password")
        role = request.data.get("role")

        if CustomUser.objects.filter(username=roll_number,role=role).exists():
            user = CustomUser.objects.get(username=roll_number,role=role)
            if UserProfile.objects.filter(user=user).exists():
                user_profile = UserProfile.objects.get(user=user)
                if user_profile.verified:
                    return Response({"error": "User already exists"}, status=400)
                else:
                    user.delete()
            else:
                user.delete()
            
        user = CustomUser.objects.create_user(username=roll_number, password=password,role=role)
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
            user = user_profile.user
            user.is_active = False
            user.save()
            user_profile.save()
            print(f"User profile: {user_profile}")
            if role == "mentee":
                Mentee.objects.create(user=user_profile)
            elif role == "mentor":
                Mentor.objects.create(user=user_profile)
            print("mail")
            send_verification_email(user_profile)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    

class RegisterUserViewSSO(APIView):
    permission_classes = [AllowAny]  

    def post(self, request):
        print(request.data)
        roll_number = request.data.get("roll_number").lower()
        password = request.data.get("password")
        role = request.data.get("role")

        if CustomUser.objects.filter(username=roll_number,role=role).exists():
            user = CustomUser.objects.get(username=roll_number,role=role)
            if UserProfile.objects.filter(user=user).exists():
                user_profile = UserProfile.objects.get(user=user)
                if user_profile.verified:
                    return Response({"error": "User already exists"}, status=400)
                else:
                    user.delete()
            else:
                user.delete()
            
        user = CustomUser.objects.create_user(username=roll_number, password=password,role=role)
        user.is_active = True

        user.save()
        mutable_copy = request.POST.copy()
        mutable_copy["user"] = user.id
        
        serializer = RegisterUserSerializer(data=mutable_copy)

        if serializer.is_valid():
            serializer.save()
            verification_token = generate_verification_token()
            user_profile = UserProfile.objects.get(user=user)
            user_profile.verification_token = verification_token
            user_profile.verified = True
            user = user_profile.user
            user.is_active = True
            user.save()
            user_profile.save()
            print(f"User profile: {user_profile}")
            if role == "mentee":
                Mentee.objects.create(user=user_profile)
            elif role == "mentor":
                Mentor.objects.create(user=user_profile)
            print("mail")
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class UserProfileView(APIView):

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




class UserAutoCompleteView(ListAPIView):
    """
    ListAPIView to access user data, for user searching
    """

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
            data = fetch_from_sso(
                request.data["code"], "http://localhost:3000/register", request
            )
        except APIException as e:
            return Response(e.detail, status=e.status_code)

        return Response(data)

from rest_framework.exceptions import AuthenticationFailed
from .customauth import RollNumberBackend
import secrets

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        mutable_copy = request.POST.copy()
        mutable_copy["username"] = mutable_copy["username"].lower()

        role = mutable_copy.get("role")
        username=mutable_copy["username"]
        if not role:
            raise AuthenticationFailed("Role is required")
        password = request.data.get("password")
        backend = RollNumberBackend()
        user= backend.authenticate(request=request, username=username, password=password, role=role)
        print(user)
        if user is None:
            raise AuthenticationFailed("Invalid roll number, password, or role")
        print(user.is_active)

        # Call the parent class to obtain the JWT token (after authentication)
        random_token = secrets.token_urlsafe(16)  # Generates a secure random string of 16 characters
        custom_token = f"{user.id}-{random_token}"

        # Optionally store the token in a model for later validation or expiration
        # Example: store token in a custom model for tracking
        # Token.objects.create(user=user, token=custom_token, expiration_date=expiration_date)

        # Response with custom token
        response_data = {
            "access": custom_token,  # This is your custom token instead of JWT
            "role": user.role,
        }
        response = JsonResponse(response_data)
        
        # Set the cookie with the custom token (make it HttpOnly for security)
        # response.set_cookie(
        #         key=SIMPLE_JWT["AUTH_COOKIE"], value=custom_token, httponly=True
        #     )

        response.set_cookie(
            key="auth", 
            value=custom_token, 
            httponly=True, 
        )
        
        # Log cookie settings for debugging
        print(f"Cookie set with value: {custom_token}")
        
        return response


class CustomSSOTokenView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        roll_number = request.data.get("username")
        role = request.data.get("role")

        if not roll_number or not role:
            raise AuthenticationFailed("Roll number and role are required")

        roll_number = roll_number.lower()

        try:
            user = CustomUser.objects.get(username=roll_number, role=role)
        except CustomUser.DoesNotExist:
            raise AuthenticationFailed("User does not exist")

        if not user.is_active:
            raise AuthenticationFailed("User is not active")

        # Generate custom token
        random_token = secrets.token_urlsafe(16)
        custom_token = f"{user.id}-{random_token}"

        response_data = {
            "access": custom_token,
            "role": user.role,
        }

        response = JsonResponse(response_data)

        # Optional: Set token as cookie
        response.set_cookie(
            key="auth",
            value=custom_token,
            httponly=True,
        )

        print(f"[SSO] Token issued for {user.username}: {custom_token}")
        return response
