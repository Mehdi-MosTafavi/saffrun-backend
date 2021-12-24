from authentication.serializers import ShortUserSerializer
from comment.models import Comment
from core.models import Image
from core.responses import ErrorResponse
from core.serializers import ImageSerializer
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from profile.models import UserProfile
from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework import serializers, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from .models import Event


class EventSerializer(FlexFieldsModelSerializer):
    category_id = serializers.IntegerField()

    class Meta:
        model = Event
        fields = [
            'title',
            "description",
            "discount",
            "category_id",
            "start_datetime",
            "end_datetime",
        ]


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
        return obj.participants.all().count()


class EventDetailImageSerializer(FlexFieldsModelSerializer):
    images = ImageSerializer(many=True)
    participants = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    is_participate = serializers.SerializerMethodField()

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
            'comments',
            "is_participate"
        ]

    def get_category(self, obj):
        return {
            'id': obj.category.id,
            'title': obj.category.name
        }

    def get_is_participate(self, obj):
        user = get_object_or_404(UserProfile, user=self.context['request'].user)

        return user in obj.participants.all()

    def get_owner(self, obj):
        return {
            'id': obj.owner.id,
            'title': obj.owner.user.username
        }

    def get_comments(self, obj):
        comments = Comment.objects.filter(event__isnull=False, is_parent=True).filter(event__id=obj.id).order_by(
            '-updated_at')
        list_comment = []
        for comment in comments[:3]:
            list_comment.append({
                "id": comment.id,
                "name": comment.user.user.last_name,
                "date": comment.created_at,
                "text": comment.content
            })
        return list_comment

    def get_participants(self, obj):
        return obj.participants.all().count()


class ManyEventSerializer(serializers.Serializer):
    events = EventSerializer(many=True)


class AllEventSerializer(serializers.Serializer):
    class SortChoices(models.TextChoices):
        TTL = "title"
        SDT = "start_datetime"

    class TypeChoices(models.TextChoices):
        ALL = "all"
        RNN = "running"
        DON = "done"

    search_query = serializers.CharField(
        max_length=200, allow_null=False, allow_blank=True
    )
    participant_id = serializers.IntegerField(required=False)
    from_datetime = serializers.DateTimeField(required=False)
    until_datetime = serializers.DateTimeField(required=False)
    sort = serializers.ChoiceField(SortChoices, default=SortChoices.TTL)
    type = serializers.ChoiceField(TypeChoices, default=TypeChoices.ALL)
    page = serializers.IntegerField()
    page_count = serializers.IntegerField()


class AddParticipantSerializer(serializers.Serializer):
    event_id = serializers.IntegerField(required=True)

    def add_participants(self, request):
        event_id = self.data.get("event_id")
        try:
            event = Event.objects.get(id=event_id)
        except ObjectDoesNotExist:
            return Response(
                {"Error": ErrorResponse.NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )
        partcipant = get_object_or_404(UserProfile, user=request.user)
        event.participants.add(partcipant.id)
        event.save()

        return Response({"status": "participant added"}, status=status.HTTP_200_OK)


class AddImageSerializer(serializers.Serializer):
    event_id = serializers.IntegerField(required=True)
    image_id = serializers.IntegerField(required=True)

    def add_image(self):
        event_id = self.data.get("event_id")
        image_id = self.data.get("image_id")
        try:
            event = Event.objects.get(id=event_id)
            image = Image.objects.get(id=image_id)
        except ObjectDoesNotExist:
            return Response(
                {"Error": ErrorResponse.NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )
        event.images.add(image)
        event.save()
        event_serializer = EventSerializer(instance=event)
        return Response(event_serializer.data, status=status.HTTP_200_OK)


class SpecificEventSerializer(FlexFieldsModelSerializer):
    image = ImageSerializer(allow_null=True)
    owner = serializers.SerializerMethodField(method_name="get_owner")

    def get_owner(self, reservation):
        return ShortUserSerializer(instance=reservation.owner.user).data

    class Meta:
        model = Event
        fields = ["id", "title", "description", "image", "owner"]
