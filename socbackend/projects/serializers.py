from rest_framework import serializers

from .models import Project, MenteePreference, Mentor, Mentee, RankList
from accounts.serializers import UserProfileSerializer


class ProjectSerializer(serializers.ModelSerializer):
    mentor_details = serializers.SerializerMethodField()
    co_mentor_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = "__all__"
        read_only_fields = ["season"]
    
    def get_mentor_details(self, obj):
        """Get linked mentor objects with phone numbers"""
        mentors = Mentor.objects.filter(projects=obj).select_related('user')
        return [{
            'name': m.user.name,
            'roll_number': m.user.roll_number,
            'phone_number': m.user.phone_number
        } for m in mentors]
    
    def get_co_mentor_details(self, obj):
        """Parse co_mentor_info to extract details (case-insensitive roll matching)"""
        import re
        if not obj.co_mentor_info or obj.co_mentor_info == 'NA':
            return []
        
        matches = re.findall(r'([A-Za-z\s]+)\s*\((\w+)\)', obj.co_mentor_info)
        co_mentors = []
        for name, roll in matches:
            # Try to get phone number from UserProfile (case-insensitive)
            try:
                from accounts.models import CustomUser, UserProfile
                user = CustomUser.objects.get(username=roll.strip().lower())
                profile = UserProfile.objects.get(user=user)
                co_mentors.append({
                    'name': name.strip(),
                    'roll_number': roll.strip(),
                    'phone_number': profile.phone_number
                })
            except:
                co_mentors.append({
                    'name': name.strip(),
                    'roll_number': roll.strip(),
                    'phone_number': 'Not available'
                })
        return co_mentors


class BasicProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["id", "title", "general_category", "banner_image", "banner_image_link", "domain"]


class MenteePreferenceSerializer(serializers.ModelSerializer):
    project = BasicProjectSerializer()

    class Meta:
        model = MenteePreference
        fields = ["id", "mentee", "project", "sop", "preference"]


class MenteePreferenceSaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenteePreference
        fields = ["id", "mentee", "project", "sop", "preference"]


class MenteeSerializer(serializers.ModelSerializer):
    user_profile = UserProfileSerializer(source="user")
    preferences = serializers.SerializerMethodField()

    class Meta:
        model = Mentee
        fields = ["user_profile", "season", "preferences"]

    def get_preferences(self, obj):
        mentor_project = self.context.get("mentor_project")
        preference = obj.menteepreference_set.filter(project=mentor_project).first()
        return MenteePreferenceSerializer(preference).data if preference else None


class MentorSerializer(serializers.ModelSerializer):
    user_profile = UserProfileSerializer(source="user")
    projects = BasicProjectSerializer(many=True)
    mentees = serializers.SerializerMethodField()

    class Meta:
        model = Mentor
        fields = ["user_profile", "season", "projects", "mentees"]

    def get_mentees(self, obj, project_id=None):
        if not project_id:
            return []
        try:
            mentees = obj.mentees(project_id)
            print(f"DEBUG: Mentees found = {mentees}")
        except Exception as e:
            print(f"ERROR: {str(e)}")
            return []

        serializer = MenteeSerializer(mentees, many=True, context={"mentor_project": project_id})
        return serializer.data


class RankListSerializer(serializers.ModelSerializer):
    mentee = serializers.SerializerMethodField()
    preference = serializers.SerializerMethodField()

    class Meta:
        model = RankList
        fields = ["mentee", "rank", "preference"]

    def get_mentee(self, obj):
        project_id = self.context.get("mentor_project")
        return MenteeSerializer(obj.mentee, context={"mentor_project": project_id}).data

    def get_preference(self, obj):
        project_id = self.context.get("mentor_project")
        preference = obj.mentee.menteepreference_set.filter(project_id=project_id).first()
        print("jk", preference)
        return MenteePreferenceSerializer(preference).data if preference else None


class RankListSaveSerializer(serializers.Serializer):
    """
    Saves/updates the unified ranklist for a project.

    FIXED: No longer mentor-scoped.
    Any mentor of the project can overwrite the full project ranklist.
    All co-mentors see the same single ranklist.
    """
    rank_list = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
    )

    def validate_rank_list(self, value):
        for entry in value:
            if "mentee_id" not in entry or "rank" not in entry:
                raise serializers.ValidationError(
                    "Each entry must contain 'mentee_id' and 'rank'."
                )
        return value

    def create(self, validated_data):
        rank_list_data = validated_data.pop("rank_list", [])
        project_id = self.context.get("project_id")

        if not project_id:
            raise serializers.ValidationError("Project ID missing.")

        try:
            mentor_project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            raise serializers.ValidationError("Project not found.")

        # Delete the ENTIRE existing ranklist for this project (all mentors share one list)
        deleted_count, _ = RankList.objects.filter(project=mentor_project).delete()
        print(f"Deleted {deleted_count} existing rank list entries for project {mentor_project.id}")

        for entry in rank_list_data:
            mentee_roll_number = entry["mentee_id"]
            rank = entry["rank"]
            preference = entry.get("preference")

            try:
                mentee = Mentee.objects.get(
                    user__roll_number=mentee_roll_number,
                    domain=mentor_project.domain,
                )
            except Mentee.DoesNotExist:
                raise serializers.ValidationError(
                    f"Mentee with roll number {mentee_roll_number} not found in this domain."
                )

            # Ensure the mentee has actually applied to this project
            if not MenteePreference.objects.filter(mentee=mentee, project=mentor_project).exists():
                raise serializers.ValidationError(
                    f"Mentee {mentee_roll_number} has not applied to this project."
                )

            # Fetch or create MenteePreference
            mentee_pref, _ = MenteePreference.objects.get_or_create(
                mentee=mentee,
                project=mentor_project,
                defaults={"preference": preference or 1},
            )

            if preference is not None:
                mentee_pref.preference = preference
                mentee_pref.save()

            # Create RankList entry — project-level, no mentor FK
            RankList.objects.create(
                project=mentor_project,
                mentee=mentee,
                preference=mentee_pref.preference,
                rank=rank,
            )
            print(f"Added mentee {mentee_roll_number} to rank list at rank {rank}")

        return {"status": "Rank list saved successfully"}
