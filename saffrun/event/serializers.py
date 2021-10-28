from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers, status
from rest_framework.response import Response

from saffrun.commons.ErrorResponse import ErrorResponse
from .models import Event


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = "__all__"


class ManyEventSerializer(serializers.Serializer):
    events = EventSerializer(many=True)


class AllEventSerializer(serializers.Serializer):
    search_query = serializers.CharField(
        max_length=200, allow_null=False, allow_blank=True
    )
    owner_id = serializers.IntegerField(required=False)
    participant_id = serializers.IntegerField(required=False)
    from_datetime = serializers.DateTimeField(required=False)
    until_datetime = serializers.DateTimeField(required=False)
    sort = serializers.ChoiceField([(1, "title"), (2, "start_date")], default=1)


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
                participant = User.objects.get(id=participant_id)
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
