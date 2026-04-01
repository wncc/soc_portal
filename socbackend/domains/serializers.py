from rest_framework import serializers

from .models import Domain, DomainMembership


class DomainSerializer(serializers.ModelSerializer):
    cover_photo_url = serializers.SerializerMethodField()
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Domain
        fields = [
            "id", "slug", "name", "description",
            "cover_photo", "cover_photo_url",
            "is_active", "mentee_reg_open", "mentor_reg_open",
            "project_creation_open", "project_editing_open",
            "order", "created_at", "member_count",
        ]
        read_only_fields = ["id", "created_at"]

    def get_cover_photo_url(self, obj):
        request = self.context.get("request")
        if obj.cover_photo and request:
            return request.build_absolute_uri(obj.cover_photo.url)
        return None

    def get_member_count(self, obj):
        return obj.memberships.filter(is_approved=True).count()


class DomainMembershipSerializer(serializers.ModelSerializer):
    domain_slug = serializers.CharField(source="domain.slug", read_only=True, allow_null=True)
    domain_name = serializers.CharField(source="domain.name", read_only=True, allow_null=True)
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = DomainMembership
        fields = [
            "id", "username", "domain_slug", "domain_name",
            "role", "is_approved", "joined",
        ]
        read_only_fields = ["id", "joined", "username", "domain_slug", "domain_name"]


class MyMembershipSerializer(serializers.ModelSerializer):
    """Compact serializer for the 'my memberships' response used in auth tokens."""
    domain = serializers.SlugField(source="domain.slug", allow_null=True)
    domain_name = serializers.CharField(source="domain.name", allow_null=True)

    class Meta:
        model = DomainMembership
        fields = ["domain", "domain_name", "role", "is_approved"]
