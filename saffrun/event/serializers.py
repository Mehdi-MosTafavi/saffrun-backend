from authentication.serializers import ShortUserSerializer
from core.models import Image
from core.responses import ErrorResponse
from core.serializers import ImageSerializer
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from profile.models import UserProfile
from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework import serializers, status
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
            "price"
        ]



class EventImageSerializer(FlexFieldsModelSerializer):
    images = ImageSerializer(many=True)
    participants = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id',
            "title",
            "description",
            "discount",
            "price",
            'participants',
            "start_datetime",
            "end_datetime",
            "category",
            "images",
        ]

    def get_category(self,obj):
        return {
            'id' : obj.category.id,
            'title' : obj.category.name
        }

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
    participants_id = serializers.ListField(
        required=True,
        allow_empty=False,
        child=serializers.IntegerField(min_value=1),
    )

    def add_participants(self):
        event_id = self.data.get("event_id")
        initial_participant_id = self.data.get("participants_id")
        try:
            event = Event.objects.get(id=event_id)
        except ObjectDoesNotExist:
            return Response(
                {"Error": ErrorResponse.NOT_FOUND},
                status=status.HTTP_404_NOT_FOUND,
            )
        verified_participant_ids = []
        for participant_id in initial_participant_id:
            try:
                participant = UserProfile.objects.get(user__id=participant_id)
            except ObjectDoesNotExist:
                return Response(
                    {"Error": ErrorResponse.NOT_FOUND},
                    status=status.HTTP_404_NOT_FOUND,
                )
            verified_participant_ids.append(participant.id)
        event.participants.add(*verified_participant_ids)
        event.save()
        event_serializer = EventSerializer(instance=event)
        return Response(event_serializer.data, status=status.HTTP_200_OK)


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
        fields = ["id", "title", "description", "image", "owner", "price"]
