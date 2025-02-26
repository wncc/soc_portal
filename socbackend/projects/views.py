from rest_framework import generics

from .models import Project,RankList
from .serializers import ProjectSerializer, BasicProjectSerializer, MenteePreferenceSerializer, MenteePreferenceSaveSerializer ,RankListSaveSerializer,RankListSerializer

# from projects.models import Season
from accounts.new import CookieJWTAuthentication2
from rest_framework import generics, views
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Mentee, Project, MenteePreference, MenteeWishlist
from rest_framework.permissions import IsAuthenticated
from accounts.models import UserProfile
from rest_framework.permissions import AllowAny
import logging

logger = logging.getLogger(__name__)
# from .serializers import (
#     ProjectAdditionSerializer,
# )

class ProjectDetailView(APIView):
    permission_classes = []
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def get(self, request, pk):
        project = Project.objects.get(pk=pk)
        serializer = self.serializer_class(project)
        return Response(serializer.data)
    

class ProjectWishlist(APIView):
    authentication_classes  = [CookieJWTAuthentication2]
    permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]  # Allow any user to access the post request

    def get(self, request):
        user_profile = UserProfile.objects.get(user=request.user)
        
        # logger.error('\n \n Error 1 \n \n ')
        mentee = Mentee.objects.get(user=user_profile)
        # logger.error('\n \n Error 2 \n \n ')
        preferences = MenteeWishlist.objects.filter(mentee=mentee)
        # logger.error('\n \n Error 3 \n \n ')
        project_objects = [preference.project for preference in preferences]
        # logger.error('\n \n Error 4 \n \n ')
        serializer = BasicProjectSerializer(project_objects, many=True)
        # logger.error('\n \n Error 5 \n \n ')
        return Response(serializer.data)
    
    def post(self, request):
        # logger.error('\n \n Error 6 \n \n ')
       # print("Request Data:", request.user)
        user_profile = UserProfile.objects.get(user=request.user)

        # logger.error('\n \n Error 7 \n \n ')
        mentee = Mentee.objects.get(user=user_profile)
        # logger.error('\n \n Error 8 \n \n ')
        project_id = request.data["project_id"]
        # logger.error('\n \n Error 9 \n \n ')
        project = Project.objects.get(pk=project_id)
        # logger.error('\n \n Error 10 \n \n ')
        preference = MenteeWishlist(mentee=mentee, project=project)
        # logger.error('\n \n Error 11 \n \n ')
        preference.save()
        # logger.error('\n \n Error 12 \n \n ')
        return Response({"message": "Project added to wishlist."})
    
    def delete(self, request):
        user_profile = UserProfile.objects.get(user=request.user)
        mentee = Mentee.objects.get(user=user_profile)
        project_id = request.GET['project_id']
        project = Project.objects.get(pk=project_id)
        preference = MenteeWishlist.objects.get(mentee=mentee, project=project)
        preference.delete()
        return Response({"message": "Project removed from wishlist."})
    
class ProjectPreference(APIView):
    authentication_classes  = [CookieJWTAuthentication2]
    permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]  # Allow any user to access the post request

    def get(self, request):
        user_profile = UserProfile.objects.get(user=request.user)
        mentee = Mentee.objects.get(user=user_profile)
        preferences = MenteePreference.objects.filter(mentee=mentee)
        serializer = MenteePreferenceSerializer(preferences, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        user_profile = UserProfile.objects.get(user=request.user)
        mentee = Mentee.objects.get(user=user_profile)
        project_id = request.data["project"]
        preference = request.data["preference"]
        sop = request.data["sop"]
        project = Project.objects.get(pk=project_id)
        serializer = MenteePreferenceSaveSerializer(data={"mentee": mentee.id, "project": project.id, "preference": preference, "sop": sop})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    def delete(self, request):
        user_profile = UserProfile.objects.get(user=request.user)
        mentee = Mentee.objects.get(user=user_profile)
        project_id = request.data["project_id"]
        project = Project.objects.get(pk=project_id)
        preference = MenteePreference.objects.get(mentee=mentee, project=project)
        preference.delete()
        return Response({"message": "Project removed from preferences."})

class BasicProjectListView(generics.ListAPIView):
    permission_classes = []
    queryset = Project.objects.all()
    serializer_class = BasicProjectSerializer

from .serializers import MentorSerializer
from .models import Mentor


class MentorProfileView(APIView):
    authentication_classes = [CookieJWTAuthentication2]  # Your custom authentication class
   # permission_classes = [IsAuthenticated]  # Ensure the user is authenticated
    permission_classes = [AllowAny]
    
    def get(self, request):
        try:
            # Fetch the mentor profile for the currently logged-in user
            mentor = request.user.mentor  # Assuming mentor has a OneToOne relationship with User
            serializer = MentorSerializer(mentor)
            # print(serializer.data)
            return Response(serializer.data)
        except Mentor.DoesNotExist:
            return Response({'error': 'You are not a mentor or mentor profile does not exist.'}, status=404)

from rest_framework import status   
class SaveRankListView(APIView):
    authentication_classes = [CookieJWTAuthentication2]  # Custom authentication
    permission_classes = [AllowAny]  # Ensure the user is authenticated

    def get(self, request, project_id):
        """ Fetch saved rank list for the authenticated mentor for a specific project """
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            mentor = Mentor.objects.get(user=user_profile)

            # Fetch the project and its rank list
            project = Project.objects.get(id=project_id)
            rank_list = RankList.objects.filter(mentor=mentor, project=project).order_by("rank")

            # Serialize the rank list and pass mentor_project context
            serializer = RankListSerializer(rank_list, many=True, context={'mentor_project': project})

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
        """ Save or update the rank list for a mentor and project """
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            mentor = Mentor.objects.get(user=user_profile)  # Ensure user is a mentor
            project = Project.objects.get(id=project_id)  # Fetch project
        except Mentor.DoesNotExist:
            return Response({'error': 'You are not a mentor or mentor profile does not exist.'}, status=404)
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found.'}, status=404)
        except Project.DoesNotExist:
            return Response({'error': 'Project not found.'}, status=404)

        # Pass mentor and project context to the serializer
        serializer = RankListSaveSerializer(data=request.data, context={'mentor': mentor, 'mentor_project': project})
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'Rank list saved successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)