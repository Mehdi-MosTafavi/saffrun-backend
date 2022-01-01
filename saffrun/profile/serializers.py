from category.serializers import CategorySerializer
from comment.serializers import CommentSerializer
from core.serializers import ImageAvatarSerializer
from core.serializers import ImageSerializer
from event.models import Event
from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework import serializers

from .models import UserProfile, Business


class FollowSerializer(serializers.Serializer):
    employee_id = serializers.IntegerField()


class EmployeeProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField("get_full_name")
    username = serializers.SerializerMethodField("get_username")

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

    class Meta:
        model = UserProfile
        fields = ["id", "username", "full_name"]


class RemoveFollowerSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()


class UpdateBusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        exclude = ('owner',)


class GetBusinessSerializer(serializers.ModelSerializer):
    owner = EmployeeProfileSerializer()
    category = CategorySerializer()
    images = ImageSerializer(many=True)

    class Meta:
        model = Business
        fields = "__all__"


class BusinessByClientReturnSerializer(GetBusinessSerializer):
    follower_count = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    events = serializers.SerializerMethodField()

    @staticmethod
    def get_follower_count(business):
        return business.owner.followers.count()

    @staticmethod
    def get_comments(business):
        serialized_comments = CommentSerializer(business.owner.comment_owner.order_by("-created_at")[:3], many=True)
        return serialized_comments.data

    @staticmethod
    def get_events(business):
        serialized_event = EventImageSerializer(business.owner.owned_event.order_by("start_datetime")[:5], many=True)
        return serialized_event.data


class EventImageSerializer(FlexFieldsModelSerializer):
    images = ImageSerializer(many=True)
    participants = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id',
            "title",
            "description",
            "discount",
            "owner",
            'participants',
            "start_datetime",
            "end_datetime",
            "category",
            "images",
        ]

    def get_category(self, obj):
        return {
            'id': obj.category.id,
            'title': obj.category.name
        }

    def get_owner(self, obj):
        return {
            'id': obj.owner.id,
            'title': obj.owner.user.username
        }

    def get_participants(self, obj):
        particpiants_list = []
        for participant in obj.participants.all():
            particpiants_list.append({
                'id': participant.id,
                'name': participant.user.username,
                'image': ImageAvatarSerializer(instance=participant.avatar).data
            })
        return particpiants_list
