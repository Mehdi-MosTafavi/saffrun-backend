from django.db.models import Q

from .models import Event


def filter_from_datetime_query(events_serializer):
    return (
        Q(start_datetime__gte=events_serializer.data.get("from_datetime"))
        if events_serializer.data.get("from_datetime")
        else Q()
    )


def filter_until_datetime_query(events_serializer):
    return (
        Q(end_datetime__lte=events_serializer.data.get("until_datetime"))
        if events_serializer.data.get("until_datetime")
        else Q()
    )


def filter_owner_query(events_serializer):
    return (
        Q(owner=events_serializer.data.get("owner_id"))
        if events_serializer.data.get("owner_id")
        else Q()
    )


def filter_participant_query(events_serializer):
    return (
        Q(participants__in=[events_serializer.data.get("participant_id")])
        if events_serializer.data.get("participant_id")
        else Q()
    )


def final_filter_query(events_serializer):
    return (
        Q(title__icontains=events_serializer.data.get("search_query"))
        & filter_from_datetime_query(events_serializer)
        & filter_until_datetime_query(events_serializer)
        & filter_owner_query(events_serializer)
        & filter_participant_query(events_serializer)
    )


def get_sorted_events(events_serializer):
    return Event.objects.filter(final_filter_query(events_serializer)).order_by(
        events_serializer.data.get("sort").value
    )


def create_an_event(validated_data, owner):
    event = Event.objects.create(
        start_datetime=validated_data["start_datetime"],
        end_datetime=validated_data["end_datetime"],
        title=validated_data["title"],
        discount=validated_data["discount"],
        owner=owner,
    )
    return event
