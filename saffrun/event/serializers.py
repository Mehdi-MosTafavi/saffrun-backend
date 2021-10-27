from django.contrib.auth.models import User
from rest_framework import serializers

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
