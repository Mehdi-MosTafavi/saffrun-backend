from core.models import Image
from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework import serializers
from versatileimagefield.serializers import VersatileImageFieldSerializer


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
