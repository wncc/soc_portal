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


class ProjectCreateView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        """ Create a new project """
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Project created successfully!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
    # permission_classes = [AllowAny]  # Allow any user to access the post request

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
    # permission_classes = [AllowAny]  # Allow any user to access the post request

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
from rest_framework import status
from django.db.models import Max

class MentorProfileView(APIView):
    authentication_classes = [CookieJWTAuthentication2]  # Your custom authentication class
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated
    # permission_classes = [AllowAny]
    
    def get(self, request,project_id=None):
        try:
            # Get mentor profile of the logged-in user
            user_profile = UserProfile.objects.get(user=request.user)
            mentor = Mentor.objects.get(user=user_profile)
            mentor_serializer = MentorSerializer(mentor, context={'request': request}) 
            if project_id:  # If project_id is provided, return mentees of that project too
                mentees = mentor_serializer.get_mentees(mentor,project_id)  # Using the mentees method
                return Response({
                    "mentor": mentor_serializer.data,
                    "mentees": mentees
                }, status=status.HTTP_200_OK)

            # If no project_id, return only mentor details
            return Response({"mentor": mentor_serializer.data}, status=status.HTTP_200_OK)

        except Mentor.DoesNotExist:
            return Response({'error': 'Mentor profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Project.DoesNotExist:
            return Response({'error': 'Project not found or does not belong to the mentor.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def post(self, request):
        try:
            # Get the mentor profile of the logged-in user
            user_profile = UserProfile.objects.get(user=request.user)
            mentor = Mentor.objects.get(user=user_profile)
            
            last_project = Project.objects.aggregate(max_id=Max('id'))['max_id']
            new_project_id = (last_project or 0) + 1
            print("id should be:",new_project_id)

            print(request.data)
            project_serializer = ProjectSerializer(data=request.data)
            if project_serializer.is_valid():
                project = project_serializer.save(id=new_project_id)  # Manually setting the ID
            else:
                return Response(project_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            if project not in mentor.projects.all():
                mentor.projects.add(project)
                mentor.save()

            return Response({
                "message": "Project linked to mentor successfully",
                "project": ProjectSerializer(project).data
            }, status=status.HTTP_200_OK)

        except Project.DoesNotExist:
            return Response({'error': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Mentor.DoesNotExist:
            return Response({'error': 'Mentor profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def put(self, request, project_id=None):
        try:
            if not project_id:
                return Response({'error': 'Project ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

            # Get the mentor profile of the logged-in user
            user_profile = UserProfile.objects.get(user=request.user)
            mentor = Mentor.objects.get(user=user_profile)

            # Get the project
            project = Project.objects.get(id=project_id)

            # Ensure the mentor owns the project
            if project not in mentor.projects.all():
                return Response({'error': 'You do not have permission to edit this project.'}, status=status.HTTP_403_FORBIDDEN)

            # Update the project using the serializer
            serializer = ProjectSerializer(project, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "message": "Project updated successfully.",
                    "project": serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Project.DoesNotExist:
            return Response({'error': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Mentor.DoesNotExist:
            return Response({'error': 'Mentor profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            
    def patch(self, request):
        """ Update only the phone number of the mentee """
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            mentee = Mentor.objects.get(user=user_profile)

            phone_number = request.data.get('phone_number')
            if phone_number is None:
                return Response({'error': 'Phone number is required.'}, status=status.HTTP_400_BAD_REQUEST)
            user_profile.phone_number = phone_number
            user_profile.save()

            serializer = MentorSerializer(mentee, context={'request': request})
            print(serializer.data)
            return Response({"mentee": serializer.data, "message": "Phone number updated successfully."}, status=status.HTTP_200_OK)

        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Mentor.DoesNotExist:
            return Response({'error': 'Mentor profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from rest_framework import status   
class SaveRankListView(APIView):
    authentication_classes = [CookieJWTAuthentication2]  # Custom authentication
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated
    # permission_classes = [AllowAny]  # Ensure the user is authenticated

    def get(self, request, project_id=None):
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
        serializer = RankListSaveSerializer(data=request.data, context={'mentor': mentor, 'project_id': project.id})
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'Rank list saved successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
        
        

import os
import requests
from django.conf import settings
from django.http import JsonResponse

def download_project_banner(request):
    file_url = request.GET.get("file_url")
    project_id = request.GET.get("id")
    if not file_url or not project_id:
        return JsonResponse({"error": "Missing file URL or project ID"}, status=400)

    projects_folder = os.path.join(settings.MEDIA_ROOT, "projects")
    os.makedirs(projects_folder, exist_ok=True)

    filename = f"{project_id}.png"
    file_path = os.path.join(projects_folder, filename)
    relative_file_path = f"projects/{filename}"  # This is the path to store in DB

    # If the file already exists, return the saved path
    if os.path.exists(file_path):
        return JsonResponse({"success": "File already exists", "file_path": relative_file_path})

    try:
        # Extract Google Drive file ID if needed
        if "drive.google.com" in file_url:
            match = file_url.split("/d/")[-1].split("/")[0]
            file_url = f"https://drive.google.com/uc?export=download&id={match}"

        response = requests.get(file_url, stream=True)
        if response.status_code != 200:
            return JsonResponse({"error": f"Failed to download file. Status code: {response.status_code}"}, status=400)

        with open(file_path, "wb") as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)

        # ✅ **Save banner path in the Project model**
        try:
            project = Project.objects.get(id=project_id)
            project.banner_image = relative_file_path  # Save the banner path
            project.save()
        except Project.DoesNotExist:
            return JsonResponse({"error": "Project not found"}, status=404)

        return JsonResponse({"success": "File saved", "file_path": relative_file_path})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
   
    
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.new import CookieJWTAuthentication2
from rest_framework.permissions import IsAuthenticated
from accounts.models import UserProfile
from .models import Mentee
from .serializers import MenteeSerializer  # You need to create this if not already created

class MenteeProfileView(APIView):
    authentication_classes = [CookieJWTAuthentication2]  # Your custom authentication
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def get(self, request):
        """ Get the mentee profile of the logged-in user """
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            mentee = Mentee.objects.get(user=user_profile)
            serializer = MenteeSerializer(mentee, context={'request': request})
            return Response({"mentee": serializer.data}, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Mentee.DoesNotExist:
            return Response({'error': 'Mentee profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request):
        """ Update only the phone number of the mentee """
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            mentee = Mentee.objects.get(user=user_profile)

            phone_number = request.data.get('phone_number')
            if phone_number is None:
                return Response({'error': 'Phone number is required.'}, status=status.HTTP_400_BAD_REQUEST)
            user_profile.phone_number = phone_number
            user_profile.save()

            serializer = MenteeSerializer(mentee, context={'request': request})
            print(serializer.data)
            return Response({"mentee": serializer.data, "message": "Phone number updated successfully."}, status=status.HTTP_200_OK)

        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Mentee.DoesNotExist:
            return Response({'error': 'Mentee profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)