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
        fields = ["id", "title", "general_category", "banner_image"]

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
    project = BasicProjectSerializer()
    mentees = serializers.SerializerMethodField()

    class Meta:
        model = Mentor
        fields = ['user_profile', 'season', 'project', 'mentees']

    def get_mentees(self, obj):
        mentees = obj.mentees.all()
        # Pass the mentor's project to the MenteeSerializer context
        serializer = MenteeSerializer(mentees, many=True, context={'mentor_project': obj.project})
        return serializer.data
    
    
class RankListSerializer(serializers.ModelSerializer):
    mentee = serializers.SerializerMethodField()
    preference = serializers.SerializerMethodField()

    class Meta:
        model = RankList
        fields = ['mentee', 'rank', 'preference']

    def get_mentee(self, obj):
        """ Use MenteeSerializer to include user profile and preferences """
        mentor_project = self.context.get('mentor_project')  # Get mentor's project
        return MenteeSerializer(obj.mentee, context={'mentor_project': mentor_project}).data

    def get_preference(self, obj):
        """ Fetch preference from MenteePreference instead of RankList """
        return obj.get_preference()
    
class RankListSaveSerializer(serializers.Serializer):
    rank_list = serializers.ListField(
        child=serializers.DictField(),
        write_only=True
    )

    def validate_rank_list(self, value):
        for entry in value:
            if 'mentee_id' not in entry or 'rank' not in entry:
                raise serializers.ValidationError(
                    "Each entry must contain 'mentee_id' and 'rank'."
                )
        return value

    def create(self, validated_data):
        rank_list_data = validated_data.pop('rank_list', [])
        mentor = self.context['mentor']

        # Step 1: ❌ Delete existing rank list entries for this mentor
        RankList.objects.filter(mentor=mentor).delete()
        print(f"Deleted existing rank list for mentor {mentor.id}")

        # Step 2: ✅ Add new rank list entries
        for entry in rank_list_data:
            mentee_roll_number = entry['mentee_id']
            rank = entry['rank']
            preference = entry.get('preference')  # Optional

            try:
                mentee = Mentee.objects.get(user__roll_number=mentee_roll_number)
                mentor_project = mentor.project

                # Fetch mentee preference for this project
                mentee_pref, _ = MenteePreference.objects.get_or_create(
                    mentee=mentee,
                    project=mentor_project,
                    defaults={'preference': preference}
                )

                # If preference is provided, update it
                if preference is not None:
                    mentee_pref.preference = preference
                    mentee_pref.save()

                # Create new rank list entry
                RankList.objects.create(
                    mentor=mentor,
                    mentee=mentee,
                    project=mentor_project,
                    preference=mentee_pref.preference,
                    rank=rank
                )

                print(f"Added mentee {mentee_roll_number} to rank list at rank {rank}")

            except Mentee.DoesNotExist:
                raise serializers.ValidationError(f"Mentee with roll number {mentee_roll_number} not found or not in your project.")

        return {'status': 'Rank list saved successfully'}

