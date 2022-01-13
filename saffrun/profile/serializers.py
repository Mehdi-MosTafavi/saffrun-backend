from core.serializers import ImageAvatarSerializer
from core.serializers import ImageSerializer
from event.models import Event
from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from .models import UserProfile, Business
from .utils import calculate_employee_rate, get_employee_rate_count


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
    
class UpdateBusinessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Business
        exclude = ('owner',)


from category.serializers import CategorySerializer
from profile.serializers import EmployeeProfileSerializer


class GetBusinessSerializer(serializers.ModelSerializer):
    owner = EmployeeProfileSerializer()
    category = CategorySerializer()
    images = ImageSerializer(many=True)
    rate = serializers.SerializerMethodField('get_rate')
    rate_count = serializers.SerializerMethodField('get_rate_count')

    @staticmethod
    def get_rate(business):
        return calculate_employee_rate(business.owner)

    @staticmethod
    def get_rate_count(business):
        return get_employee_rate_count(business.owner)

    class Meta:
        model = Business
        fields = "__all__"


from comment.serializers import CommentSerializer


class BusinessByClientReturnSerializer(GetBusinessSerializer):
    follower_count = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    events = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()

    def get_is_following(self, bussiness):
        user = get_object_or_404(UserProfile, user=self.context['request'].user)
        return user in bussiness.owner.followers.all()

    @staticmethod
    def get_follower_count(business):
        return business.owner.followers.count()

    @staticmethod
    def get_comments(business):
        serialized_comments = CommentSerializer(
            business.owner.comment_owner.filter(is_parent=True).order_by("-created_at")[:3], many=True)
        return serialized_comments.data

    @staticmethod
    def get_events(business):
        serialized_event = EventImageSerializer(business.owner.owned_event.order_by("start_datetime")[:5], many=True)
        return serialized_event.data


class EventReserveSerializer(serializers.Serializer):
    event = serializers.IntegerField()
    reserve = serializers.IntegerField()

class RateBusinessPostSerializer(serializers.Serializer):
    employee_id = serializers.IntegerField()
    rate = serializers.FloatField()

class RateBusinessReturnSerializer(serializers.Serializer):
    new_rate = serializers.IntegerField()


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
