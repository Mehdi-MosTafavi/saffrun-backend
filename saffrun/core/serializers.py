from core.models import Image
from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from versatileimagefield.serializers import VersatileImageFieldSerializer

from .models import Business
from profile.models import UserProfile


class ImageSerializer(FlexFieldsModelSerializer):
    image = VersatileImageFieldSerializer(
        sizes=[
            ("full_size", "url"),
            ("thumbnail", "thumbnail__100x100"),
        ],
        allow_null=True,
        allow_empty_file=True,
        required=False,
    )

    class Meta:
        ref_name = "image_serializer"
        model = Image
        fields = ["id", "image"]


class ImageAvatarSerializer(FlexFieldsModelSerializer):
    image = VersatileImageFieldSerializer(
        sizes=[
            ("thumbnail", "thumbnail__100x100"),
        ],
        allow_null=True,
        allow_empty_file=True,
        required=False,
    )

    class Meta:
        ref_name = "image_serializer"
        model = Image
        fields = ["image"]


class HomepageResponse(serializers.Serializer):
    image = serializers.DictField()
    first_name = serializers.CharField(allow_blank=True)
    last_name = serializers.CharField(allow_blank=True)
    followers = serializers.IntegerField(min_value=0)
    number_of_events = serializers.IntegerField(min_value=0)
    number_of_active_events = serializers.IntegerField(min_value=0)
    rate = serializers.FloatField(min_value=0)
    number_user_rate = serializers.IntegerField(min_value=0)
    number_of_comments = serializers.IntegerField(min_value=0)
    number_of_user_comments = serializers.IntegerField(min_value=0)
    last_comments = serializers.ListField(min_length=0, max_length=3, child=serializers.DictField())
    number_of_all_reserves = serializers.IntegerField(min_value=0)
    number_of_given_reserves = serializers.IntegerField(min_value=0)
    monthly_reserves = serializers.ListField(min_length=0, max_length=12, child=serializers.DictField())
    monthly_events = serializers.ListField(min_length=0, max_length=12, child=serializers.DictField())
    last_given_reserves = serializers.ListField(min_length=0, max_length=5, child=serializers.DictField())
    last_events = serializers.ListField(min_length=0, max_length=5, allow_empty=True, child=serializers.DictField())


class HomepageResponseClient(serializers.Serializer):
    list_event = serializers.ListField(min_length=0, max_length=3, child=serializers.DictField())
    list_reserve = serializers.ListField(min_length=0, max_length=3, child=serializers.DictField())


class GetAllSerializer(serializers.Serializer):
    page = serializers.IntegerField()
    page_count = serializers.IntegerField()


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

    class Meta:
        model = Business
        fields = "__all__"


from comment.serializers import CommentSerializer
from event.serializers import EventImageSerializer


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
        serialized_comments = CommentSerializer(business.owner.comment_owner.order_by("-created_at")[:3], many=True)
        return serialized_comments.data

    @staticmethod
    def get_events(business):
        serialized_event = EventImageSerializer(business.owner.owned_event.order_by("start_datetime")[:5], many=True)
        return serialized_event.data
