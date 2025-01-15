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

        # Loop over each entry in the rank_list data
        for entry in rank_list_data:
            mentee_roll_number = entry['mentee_id']  # The mentee_id now refers to the roll number
            rank = entry['rank']
            # Find the mentee by their roll number and ensure they belong to the mentor's project
            try:
                mentee = Mentee.objects.get(user__roll_number=mentee_roll_number)

                existing_entry = RankList.objects.filter(mentor=mentor, rank=rank).first()
            
                if existing_entry:
                    # If there's a clash, delete the previous entry
                    print(f"Deleting previous rank list entry for mentee {existing_entry.mentee.user.roll_number} due to rank clash.")
                    existing_entry.delete()

                # Check if the RankList entry already exists
                rank_list_entry, created = RankList.objects.update_or_create(
                    mentor=mentor,
                    mentee=mentee,
                    project=mentor.project,
                    defaults={'rank': rank}  # Update the rank if the entry exists
                )

                # If created is False, it means the entry was updated
                if created:
                    print(f"Created new rank list entry for mentee {mentee_roll_number}.")
                else:
                    print(f"Updated rank for mentee {mentee_roll_number}.")

            except Mentee.DoesNotExist:
                raise serializers.ValidationError(f"Mentee with roll number {mentee_roll_number} not found or not in your project.")

        return {'status': 'Rank list saved successfully'}


# class MentorRequestSerializer(serializers.ModelSerializer):
#     project = ProjectSerializer()

#     class Meta:
#         model = MentorRequest
#         exclude = ["mentor"]


# class ProjectAdditionSerializer(ProjectSerializer):
#     """
#     Note: this serializer has a nested project.mentors field, but since this is
#     read_only and co_mentors is write_only, this does not cause any issues.
#     """

#     class Meta:
#         model = Project
#         fields = "__all__"
#         read_only_fields = ["season", "mentors"]

#     # co_mentors = serializers.ListField(
#     #     child=serializers.IntegerField(), write_only=True, required=False
#     # )

#     def create(self, validated_data):
#         # co_mentors = validated_data.pop("co_mentors", [])
#         project = Project.objects.create(**validated_data)

#         first_mentor = self.context["request"].user
#         project.mentors.add(
#             first_mentor,
#             through_defaults={
#                 "status": MentorRequest.RequestStatusChoices.FIRST_MENTOR
#             },
#         )

#         # if len(co_mentors):
#         #     project.mentors.add(*co_mentors)

#         return project
