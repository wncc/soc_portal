from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.db import transaction

from .models import UserProfile
from .models import CustomUser
from .options import DepartmentChoices
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "role",
        ]
        extra_kwargs = {
            "password": {"style": {"input_type": "password"}, "write_only": True}
        }

    def validate_password(self, password):
        """
        Validate the password against all password validators.
        """
        validate_password(password)

        return password
    
    def validate_role(self, role):
        if role not in ['mentor', 'mentee']:
            raise serializers.ValidationError("Role must be either 'mentor' or 'mentee'")
        return role


class RegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        exclude = ["verified", "verification_token"]
        extra_kwargs = {
            "password": {"style": {"input_type": "password"}, "write_only": True}
        }
    def create(self, validated_data):
        user_instance = validated_data.pop('user')
        print("User Instance:", user_instance)  # Just for debugging

        # Create user data dictionary based on the fields you expect
        if isinstance(user_instance, CustomUser):
        # Directly access the attributes of user_instance
            user = user_instance
        else:
            # Handle error case if user_instance is not a valid CustomUser
            raise serializers.ValidationError("Invalid user data")

        # Now create the user profile
        return UserProfile.objects.create(user=user, **validated_data)

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        exclude = ["user", "verified",  "verification_token"]
        extra_kwargs = {
            "roll_number": {"read_only": True}
        }

    # def create(self, validated_data):
    #     """
    #     Override the create method with objects.create_user,
    #     since the former saves with an unencrypted password
    #     """
    #     return User.objects.create_user(validated_data)


class RegisterUserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = UserProfile
        fields = "__all__"
        # extra_kwargs = {
        #     "password": {"style": {"input_type": "password"}, "write_only": True}
        # }

    @transaction.atomic
    def create(self, validated_data):
        """
        Override the create method with objects.create_user,
        since the former saves with an unencrypted password
        """
        user_data = validated_data.pop("user")
        user = CustomUser.objects.create_user(**user_data)
        return UserProfile.objects.create(user=user, **validated_data)


class UserAutoCompleteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="user.id")
    name = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ["id", "roll_number", "name"]

    def get_name(self, obj):
        return obj.user.get_full_name()
