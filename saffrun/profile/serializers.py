from rest_framework import serializers

from .models import UserProfile


class FollowSerializer(serializers.Serializer):
    employee_id = serializers.IntegerField()


class EmployeeProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField("get_full_name")
    username = serializers.SerializerMethodField("get_username")
    title = serializers.SerializerMethodField("get_title")

    @staticmethod
    def get_full_name(user_profile):
        first = user_profile.user.first_name
        last = user_profile.user.last_name
        if first or last:
            return first + (" " if (first and last) else "") + last
        return None

    @staticmethod
    def get_username(user_profile):
        return user_profile.user.username

    @staticmethod
    def get_title(user_profile):
        print(user_profile.business)
        return user_profile.business.title if user_profile.business is not None else user_profile.user.last_name

    class Meta:
        model = UserProfile
        fields = ["id", "username", "full_name", "title"]


class RemoveFollowerSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
