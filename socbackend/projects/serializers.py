from rest_framework import serializers

from .models import Project, MenteePreference , Mentor , Mentee ,RankList
from accounts.serializers import UserProfileSerializer

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"
        read_only_fields = ["season"]


class BasicProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["id", "title", "general_category", "banner_image","banner_image_link"]

class MenteePreferenceSerializer(serializers.ModelSerializer):
    project = BasicProjectSerializer()

    class Meta:
        model = MenteePreference
        fields = "__all__"

class MenteePreferenceSaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenteePreference
        fields = "__all__"

class MenteeSerializer(serializers.ModelSerializer):
    user_profile = UserProfileSerializer(source='user')
    preferences = serializers.SerializerMethodField()

    class Meta:
        model = Mentee
        fields = ['user_profile', 'season', 'preferences']

    def get_preferences(self, obj):
        # Get the mentor's project from the context
        mentor_project = self.context.get('mentor_project')
        # Find the preference related to the mentor's project
        preference = obj.menteepreference_set.filter(project=mentor_project).first()
        return MenteePreferenceSerializer(preference).data if preference else None
    
class MentorSerializer(serializers.ModelSerializer):
    user_profile = UserProfileSerializer(source='user')
    projects = BasicProjectSerializer(many=True)
    mentees = serializers.SerializerMethodField()

    class Meta:
        model = Mentor
        fields = ['user_profile', 'season', 'projects','mentees']

    def get_mentees(self, obj,project_id=None):

        if not project_id:
            return []  # No project_id provided, return empty list

        try:
            mentees = obj.mentees(project_id)  # Call the Mentor model method
            
            print(f"DEBUG: Mentees found = {mentees}")  # Debugging
        except Exception as e:
            print(f"ERROR: {str(e)}")  # Log any unexpected errors
            return []

        serializer = MenteeSerializer(mentees, many=True,context={'mentor_project': project_id})
        return serializer.data

    
class RankListSerializer(serializers.ModelSerializer):
    mentee = serializers.SerializerMethodField()
    preference = serializers.SerializerMethodField()

    class Meta:
        model = RankList
        fields = ['mentee', 'rank', 'preference']

    def get_mentee(self, obj):
        """ Use MenteeSerializer to include user profile and preferences """
        project_id = self.context.get("mentor_project")  # Get project_id from context
        if not project_id:
            print("Error: project_id is missing in context")

        return MenteeSerializer(obj.mentee, context={'mentor_project': project_id}).data

    def get_preference(self, obj):
        """ Fetch preference from MenteePreference for the specific project instead of RankList """
        project_id = self.context.get("mentor_project")  # Get project_id from context

        if not project_id:
            print("Error: project_id is missing in context")

        # ✅ Fetch preference for the given project_id
        preference = obj.mentee.menteepreference_set.filter(project_id=project_id).first()
        print("jk", preference)
        return MenteePreferenceSerializer(preference).data if preference else None
    
    
class RankListSaveSerializer(serializers.Serializer):
    rank_list = serializers.ListField(
        child=serializers.DictField(),
        write_only=True
    )

    def validate_rank_list(self, value):
        """ Validate that each entry contains required fields. """
        for entry in value:
            if 'mentee_id' not in entry or 'rank' not in entry:
                raise serializers.ValidationError(
                    "Each entry must contain 'mentee_id' and 'rank'."
                )
        return value

    def create(self, validated_data):
        rank_list_data = validated_data.pop('rank_list', [])
        mentor = self.context.get('mentor')  # ✅ Fetch Mentor from context
        project_id = self.context.get('project_id')  # ✅ Get project_id from context

        print(mentor,project_id)
        if not mentor or not project_id:
            raise serializers.ValidationError("Mentor or Project ID missing.")

        # ✅ Fetch the correct Project instance
        try:
            mentor_project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            raise serializers.ValidationError("Project not found.")

        # ✅ Delete existing RankList entries for this mentor and project
        RankList.objects.filter(mentor=mentor, project=mentor_project).delete()
        print(f"Deleted existing rank list for mentor {mentor.id} and project {mentor_project.id}")

        # ✅ Add new RankList entries
        for entry in rank_list_data:
            mentee_roll_number = entry['mentee_id']
            rank = entry['rank']
            preference = entry.get('preference')  # Optional

            try:
                # ✅ Fetch mentee by roll number
                mentee = Mentee.objects.get(user__roll_number=mentee_roll_number)

                # ✅ Ensure the mentee is assigned to the same project
                if not MenteePreference.objects.filter(mentee=mentee, project=mentor_project).exists():
                    raise serializers.ValidationError(f"Mentee {mentee_roll_number} is not assigned to this project.")

                # ✅ Fetch or create MenteePreference
                mentee_pref, _ = MenteePreference.objects.get_or_create(
                    mentee=mentee,
                    project=mentor_project,
                    defaults={'preference': preference}
                )

                # ✅ If preference is provided, update it
                if preference is not None:
                    mentee_pref.preference = preference
                    mentee_pref.save()
                
                # ✅ Create RankList entry (Do NOT include `preference` field)
                RankList.objects.create(
                    mentor=mentor,
                    mentee=mentee,
                    project=mentor_project,
                    preference=mentee_pref.preference,
                    rank=rank
                )

                print(f"Added mentee {mentee_roll_number} to rank list at rank {rank}")

            except Mentee.DoesNotExist:
                raise serializers.ValidationError(f"Mentee with roll number {mentee_roll_number} not found.")

        return {'status': 'Rank list saved successfully'}
