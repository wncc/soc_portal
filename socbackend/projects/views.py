import os
import requests

from django.conf import settings
from django.db.models import Max, Count
from django.http import JsonResponse

from rest_framework import generics, status, views
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.new import CookieJWTAuthentication2
from accounts.models import UserProfile
from domains.models import Domain

import logging

logger = logging.getLogger(__name__)

from .models import (
    Mentee, Project, MenteePreference, MenteeWishlist, Mentor, RankList
)
from .serializers import (
    ProjectSerializer, BasicProjectSerializer,
    MenteePreferenceSerializer, MenteePreferenceSaveSerializer,
    RankListSaveSerializer, RankListSerializer,
    MentorSerializer, MenteeSerializer,
)


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def get_domain_or_404(slug):
    """Return Domain object by slug or None. Views call this and return 404 themselves."""
    try:
        return Domain.objects.get(slug=slug, is_active=True)
    except Domain.DoesNotExist:
        return None


# ---------------------------------------------------------------------------
# Project Views
# ---------------------------------------------------------------------------

class ProjectCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """Create a new project (legacy endpoint)."""
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Project created successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectDetailView(APIView):
    permission_classes = []
    serializer_class = ProjectSerializer

    def get(self, request, pk):
        try:
            project = Project.objects.get(pk=pk)
        except Project.DoesNotExist:
            return Response({"error": "Project not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(project)
        return Response(serializer.data)


class BasicProjectListView(generics.ListAPIView):
    """
    List projects.
    Optionally scoped to a domain via ?domain=<slug> query param.
    The legacy /api/projects/ route returns all projects if no filter is given.
    """
    permission_classes = []
    serializer_class = BasicProjectSerializer

    def get_queryset(self):
        domain_slug = self.request.query_params.get("domain")
        if domain_slug:
            return Project.objects.filter(domain__slug=domain_slug)
        return Project.objects.all()


class DomainProjectListView(APIView):
    """
    GET /api/domains/<slug>/projects/
    List all projects scoped to a specific domain.
    """
    permission_classes = []

    def get(self, request, slug):
        domain = get_domain_or_404(slug)
        if not domain:
            return Response({"error": "Domain not found."}, status=status.HTTP_404_NOT_FOUND)

        projects = Project.objects.filter(domain=domain)
        serializer = BasicProjectSerializer(projects, many=True)
        return Response(serializer.data)


# ---------------------------------------------------------------------------
# Wishlist Views
# ---------------------------------------------------------------------------

class ProjectWishlist(APIView):
    authentication_classes = [CookieJWTAuthentication2]
    permission_classes = [IsAuthenticated]

    def _get_mentee(self, request, domain=None):
        user_profile = UserProfile.objects.get(user=request.user)
        if domain:
            return Mentee.objects.get(user=user_profile, domain=domain)
        return Mentee.objects.get(user=user_profile)

    def get(self, request):
        domain_slug = request.query_params.get("domain")
        if not domain_slug:
            return Response({"error": "Domain parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        domain = get_domain_or_404(domain_slug)
        if not domain:
            return Response({"error": "Domain not found."}, status=status.HTTP_404_NOT_FOUND)
        
        user_profile = UserProfile.objects.get(user=request.user)
        try:
            mentee = Mentee.objects.get(user=user_profile, domain=domain)
        except Mentee.DoesNotExist:
            return Response({"error": "You are not a mentee in this domain."}, status=status.HTTP_404_NOT_FOUND)
        
        preferences = MenteeWishlist.objects.filter(mentee=mentee)
        project_objects = [pref.project for pref in preferences]
        serializer = BasicProjectSerializer(project_objects, many=True)
        return Response(serializer.data)

    def post(self, request):
        domain_slug = request.data.get("domain") or request.query_params.get("domain")
        if not domain_slug:
            return Response({"error": "Domain parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        domain = get_domain_or_404(domain_slug)
        if not domain:
            return Response({"error": "Domain not found."}, status=status.HTTP_404_NOT_FOUND)
        
        user_profile = UserProfile.objects.get(user=request.user)
        try:
            mentee = Mentee.objects.get(user=user_profile, domain=domain)
        except Mentee.DoesNotExist:
            return Response({"error": "You are not a mentee in this domain."}, status=status.HTTP_404_NOT_FOUND)
        
        project_id = request.data["project_id"]
        project = Project.objects.get(pk=project_id)
        preference = MenteeWishlist(mentee=mentee, project=project)
        preference.save()
        return Response({"message": "Project added to wishlist."})

    def delete(self, request):
        domain_slug = request.query_params.get("domain") or request.data.get("domain")
        if not domain_slug:
            return Response({"error": "Domain parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        domain = get_domain_or_404(domain_slug)
        if not domain:
            return Response({"error": "Domain not found."}, status=status.HTTP_404_NOT_FOUND)
        
        user_profile = UserProfile.objects.get(user=request.user)
        try:
            mentee = Mentee.objects.get(user=user_profile, domain=domain)
        except Mentee.DoesNotExist:
            return Response({"error": "You are not a mentee in this domain."}, status=status.HTTP_404_NOT_FOUND)
        
        project_id = request.GET["project_id"]
        project = Project.objects.get(pk=project_id)
        preference = MenteeWishlist.objects.get(mentee=mentee, project=project)
        preference.delete()
        return Response({"message": "Project removed from wishlist."})


# ---------------------------------------------------------------------------
# Preference Views
# ---------------------------------------------------------------------------

class ProjectPreference(APIView):
    authentication_classes = [CookieJWTAuthentication2]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        domain_slug = request.query_params.get("domain")
        if not domain_slug:
            return Response({"error": "Domain parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        domain = get_domain_or_404(domain_slug)
        if not domain:
            return Response({"error": "Domain not found."}, status=status.HTTP_404_NOT_FOUND)
        
        user_profile = UserProfile.objects.get(user=request.user)
        try:
            mentee = Mentee.objects.get(user=user_profile, domain=domain)
        except Mentee.DoesNotExist:
            return Response({"error": "You are not a mentee in this domain."}, status=status.HTTP_404_NOT_FOUND)
        
        preferences = MenteePreference.objects.filter(mentee=mentee).order_by('preference')
        serializer = MenteePreferenceSerializer(preferences, many=True)
        return Response(serializer.data)

    def post(self, request):
        domain_slug = request.data.get("domain") or request.query_params.get("domain")
        if not domain_slug:
            return Response({"error": "Domain parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        domain = get_domain_or_404(domain_slug)
        if not domain:
            return Response({"error": "Domain not found."}, status=status.HTTP_404_NOT_FOUND)
        
        user_profile = UserProfile.objects.get(user=request.user)
        try:
            mentee = Mentee.objects.get(user=user_profile, domain=domain)
        except Mentee.DoesNotExist:
            return Response({"error": "You are not a mentee in this domain."}, status=status.HTTP_404_NOT_FOUND)
        
        project_id = request.data.get("project")
        preference = request.data.get("preference")
        sop = request.data.get("sop", "").strip()
        
        # Validation
        if not project_id:
            return Response({"error": "Project is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not sop:
            return Response({"error": "SOP is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            project = Project.objects.get(pk=project_id, domain=domain)
        except Project.DoesNotExist:
            return Response({"error": "Project not found in this domain."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = MenteePreferenceSaveSerializer(
            data={"mentee": mentee.id, "project": project.id, "preference": preference, "sop": sop}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def delete(self, request):
        domain_slug = request.data.get("domain") or request.query_params.get("domain")
        if not domain_slug:
            return Response({"error": "Domain parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        domain = get_domain_or_404(domain_slug)
        if not domain:
            return Response({"error": "Domain not found."}, status=status.HTTP_404_NOT_FOUND)
        
        user_profile = UserProfile.objects.get(user=request.user)
        try:
            mentee = Mentee.objects.get(user=user_profile, domain=domain)
        except Mentee.DoesNotExist:
            return Response({"error": "You are not a mentee in this domain."}, status=status.HTTP_404_NOT_FOUND)
        
        project_id = request.data["project_id"]
        project = Project.objects.get(pk=project_id)
        preference = MenteePreference.objects.get(mentee=mentee, project=project)
        preference.delete()
        return Response({"message": "Project removed from preferences."})


# ---------------------------------------------------------------------------
# Mentor Profile Views
# ---------------------------------------------------------------------------

class MentorProfileView(APIView):
    authentication_classes = [CookieJWTAuthentication2]
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id=None):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            domain_slug = request.query_params.get("domain")
            domain = get_domain_or_404(domain_slug) if domain_slug else None

            # Get mentor profile — scoped to domain if provided
            if domain:
                mentor = Mentor.objects.get(user=user_profile, domain=domain)
            else:
                mentor = Mentor.objects.filter(user=user_profile).first()
                if not mentor:
                    raise Mentor.DoesNotExist

            mentor_serializer = MentorSerializer(mentor, context={"request": request})

            if project_id:
                mentees = mentor_serializer.get_mentees(mentor, project_id)
                return Response({"mentor": mentor_serializer.data, "mentees": mentees}, status=status.HTTP_200_OK)

            return Response({"mentor": mentor_serializer.data}, status=status.HTTP_200_OK)

        except Mentor.DoesNotExist:
            return Response({"error": "Mentor profile not found."}, status=status.HTTP_404_NOT_FOUND)
        except UserProfile.DoesNotExist:
            return Response({"error": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)
        except Project.DoesNotExist:
            return Response({"error": "Project not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            domain_slug = request.data.get("domain") or request.query_params.get("domain")
            domain = get_domain_or_404(domain_slug) if domain_slug else None

            if domain:
                mentor = Mentor.objects.get(user=user_profile, domain=domain)
            else:
                mentor = Mentor.objects.filter(user=user_profile).first()
                if not mentor:
                    raise Mentor.DoesNotExist

            last_project = Project.objects.aggregate(max_id=Max("id"))["max_id"]
            new_project_id = (last_project or 0) + 1
            print("id should be:", new_project_id)

            project_data = request.data.copy()
            if domain:
                project_data["domain"] = domain.id

            project_serializer = ProjectSerializer(data=project_data)
            if project_serializer.is_valid():
                project = project_serializer.save(id=new_project_id)
            else:
                return Response(project_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            if project not in mentor.projects.all():
                mentor.projects.add(project)
                mentor.save()

            return Response(
                {"message": "Project linked to mentor successfully", "project": ProjectSerializer(project).data},
                status=status.HTTP_200_OK,
            )

        except Project.DoesNotExist:
            return Response({"error": "Project not found."}, status=status.HTTP_404_NOT_FOUND)
        except Mentor.DoesNotExist:
            return Response({"error": "Mentor profile not found."}, status=status.HTTP_404_NOT_FOUND)
        except UserProfile.DoesNotExist:
            return Response({"error": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, project_id=None):
        try:
            if not project_id:
                return Response({"error": "Project ID is required."}, status=status.HTTP_400_BAD_REQUEST)

            user_profile = UserProfile.objects.get(user=request.user)
            domain_slug = request.query_params.get("domain")
            domain = get_domain_or_404(domain_slug) if domain_slug else None

            if domain:
                mentor = Mentor.objects.get(user=user_profile, domain=domain)
            else:
                mentor = Mentor.objects.filter(user=user_profile).first()
                if not mentor:
                    raise Mentor.DoesNotExist

            project = Project.objects.get(id=project_id)

            if project not in mentor.projects.all():
                return Response(
                    {"error": "You do not have permission to edit this project."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            serializer = ProjectSerializer(project, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Project updated successfully.", "project": serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Project.DoesNotExist:
            return Response({"error": "Project not found."}, status=status.HTTP_404_NOT_FOUND)
        except Mentor.DoesNotExist:
            return Response({"error": "Mentor profile not found."}, status=status.HTTP_404_NOT_FOUND)
        except UserProfile.DoesNotExist:
            return Response({"error": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request):
        """Update phone number."""
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            domain_slug = request.query_params.get("domain")
            domain = get_domain_or_404(domain_slug) if domain_slug else None

            if domain:
                mentor = Mentor.objects.get(user=user_profile, domain=domain)
            else:
                mentor = Mentor.objects.filter(user=user_profile).first()
                if not mentor:
                    raise Mentor.DoesNotExist

            phone_number = request.data.get("phone_number")
            if phone_number is None:
                return Response({"error": "Phone number is required."}, status=status.HTTP_400_BAD_REQUEST)
            user_profile.phone_number = phone_number
            user_profile.save()

            serializer = MentorSerializer(mentor, context={"request": request})
            return Response({"mentor": serializer.data, "message": "Phone number updated."}, status=status.HTTP_200_OK)

        except UserProfile.DoesNotExist:
            return Response({"error": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)
        except Mentor.DoesNotExist:
            return Response({"error": "Mentor profile not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ---------------------------------------------------------------------------
# RankList Views — FIXED: project-level, no mentor FK
# ---------------------------------------------------------------------------

class SaveRankListView(APIView):
    authentication_classes = [CookieJWTAuthentication2]
    permission_classes = [IsAuthenticated]

    def get(self, request, project_id=None):
        """
        Fetch the project-level rank list.
        Any mentor linked to the project can fetch it.
        """
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            project = Project.objects.get(id=project_id)

            # Verify caller is a mentor of this project
            domain_slug = request.query_params.get("domain")
            domain = get_domain_or_404(domain_slug) if domain_slug else project.domain
            mentor = Mentor.objects.get(user=user_profile, domain=domain)

            if project not in mentor.projects.all():
                return Response(
                    {"error": "You are not a mentor of this project."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            rank_list = RankList.objects.filter(project=project).order_by("rank")
            serializer = RankListSerializer(rank_list, many=True, context={"mentor_project": project})
            return Response({"rank_list": serializer.data}, status=status.HTTP_200_OK)

        except Mentor.DoesNotExist:
            return Response({"error": "Mentor profile not found."}, status=status.HTTP_404_NOT_FOUND)
        except UserProfile.DoesNotExist:
            return Response({"error": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)
        except Project.DoesNotExist:
            return Response({"error": "Project not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, project_id):
        """
        Save or replace the rank list for a project.
        Any mentor of the project can do this — all share one list.
        Co-mentor conflict is eliminated.
        """
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            project = Project.objects.get(id=project_id)

            domain_slug = request.query_params.get("domain") or request.data.get("domain")
            domain = get_domain_or_404(domain_slug) if domain_slug else project.domain

            # Verify caller is a mentor of this project
            mentor = Mentor.objects.get(user=user_profile, domain=domain)
            if project not in mentor.projects.all():
                return Response(
                    {"error": "You are not a mentor of this project."},
                    status=status.HTTP_403_FORBIDDEN,
                )

        except Mentor.DoesNotExist:
            return Response({"error": "You are not a mentor or mentor profile does not exist."}, status=404)
        except UserProfile.DoesNotExist:
            return Response({"error": "User profile not found."}, status=404)
        except Project.DoesNotExist:
            return Response({"error": "Project not found."}, status=404)

        # No mentor in context — project-level saving
        serializer = RankListSaveSerializer(data=request.data, context={"project_id": project.id})
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "Rank list saved successfully"}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------------------------------------------------------------------------
# Mentee Profile Views
# ---------------------------------------------------------------------------

class MenteeProfileView(APIView):
    authentication_classes = [CookieJWTAuthentication2]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            domain_slug = request.query_params.get("domain")
            domain = get_domain_or_404(domain_slug) if domain_slug else None

            if domain:
                mentee = Mentee.objects.get(user=user_profile, domain=domain)
            else:
                mentee = Mentee.objects.filter(user=user_profile).first()
                if not mentee:
                    raise Mentee.DoesNotExist

            serializer = MenteeSerializer(mentee, context={"request": request})
            return Response({"mentee": serializer.data}, status=status.HTTP_200_OK)

        except UserProfile.DoesNotExist:
            return Response({"error": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)
        except Mentee.DoesNotExist:
            return Response({"error": "Mentee profile not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            domain_slug = request.query_params.get("domain")
            domain = get_domain_or_404(domain_slug) if domain_slug else None

            if domain:
                mentee = Mentee.objects.get(user=user_profile, domain=domain)
            else:
                mentee = Mentee.objects.filter(user=user_profile).first()
                if not mentee:
                    raise Mentee.DoesNotExist

            phone_number = request.data.get("phone_number")
            if phone_number is None:
                return Response({"error": "Phone number is required."}, status=status.HTTP_400_BAD_REQUEST)
            user_profile.phone_number = phone_number
            user_profile.save()

            serializer = MenteeSerializer(mentee, context={"request": request})
            return Response({"mentee": serializer.data, "message": "Phone number updated."}, status=status.HTTP_200_OK)

        except UserProfile.DoesNotExist:
            return Response({"error": "User profile not found."}, status=status.HTTP_404_NOT_FOUND)
        except Mentee.DoesNotExist:
            return Response({"error": "Mentee profile not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ---------------------------------------------------------------------------
# Banner Download
# ---------------------------------------------------------------------------

def download_project_banner(request):
    file_url = request.GET.get("file_url")
    project_id = request.GET.get("id")
    if not file_url or not project_id:
        return JsonResponse({"error": "Missing file URL or project ID"}, status=400)

    projects_folder = os.path.join(settings.MEDIA_ROOT, "projects")
    os.makedirs(projects_folder, exist_ok=True)

    filename = f"{project_id}.png"
    file_path = os.path.join(projects_folder, filename)
    relative_file_path = f"projects/{filename}"

    if os.path.exists(file_path):
        return JsonResponse({"success": "File already exists", "file_path": relative_file_path})

    try:
        if "drive.google.com" in file_url:
            match = file_url.split("/d/")[-1].split("/")[0]
            file_url = f"https://drive.google.com/uc?export=download&id={match}"

        response = requests.get(file_url, stream=True)
        if response.status_code != 200:
            return JsonResponse({"error": f"Failed to download file. Status code: {response.status_code}"}, status=400)

        with open(file_path, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)

        try:
            project = Project.objects.get(id=project_id)
            project.banner_image = relative_file_path
            project.save()
        except Project.DoesNotExist:
            return JsonResponse({"error": "Project not found"}, status=404)

        return JsonResponse({"success": "File saved", "file_path": relative_file_path})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# ---------------------------------------------------------------------------
# Sorted Wishlist
# ---------------------------------------------------------------------------

class SortedProjectWishlist(APIView):
    authentication_classes = [CookieJWTAuthentication2]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        domain_slug = request.query_params.get("domain")
        domain = get_domain_or_404(domain_slug) if domain_slug else None

        if domain:
            all_projects = Project.objects.filter(domain=domain)
        else:
            all_projects = Project.objects.all()

        if domain:
            # Only count wishlists from mentees in this domain
            domain_mentees = Mentee.objects.filter(domain=domain)
            preferences = MenteeWishlist.objects.filter(project__in=all_projects, mentee__in=domain_mentees)
        else:
            preferences = MenteeWishlist.objects.filter(project__in=all_projects)
        
        project_counts = preferences.values("project").annotate(count=Count("project")).order_by("-count")

        projects_with_counts = []
        for project in all_projects:
            count = next((item["count"] for item in project_counts if item["project"] == project.id), 0)
            projects_with_counts.append((project, count))

        sorted_projects = [p[0] for p in sorted(projects_with_counts, key=lambda x: x[1], reverse=True)]
        serializer = BasicProjectSerializer(sorted_projects, many=True)
        return Response(serializer.data)