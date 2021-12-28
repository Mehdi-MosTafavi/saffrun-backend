from category.models import Category
from django.db.models import Q
from django.utils import timezone
from profile.models import UserProfile
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request

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


def filter_owner_query(owner):
    return Q(owner=owner)


def filter_participant_query(events_serializer):
    return (
        Q(participants__in=[events_serializer.data.get("participant_id")])
        if events_serializer.data.get("participant_id")
        else Q()
    )


def filter_type_query(events_serializer):
    if events_serializer.data.get("type").value == "all":
        return Q()
    if events_serializer.data.get("type").value == "running":
        return Q(start_datetime__lt=timezone.datetime.now()) & Q(end_datetime__gt=timezone.datetime.now())
    if events_serializer.data.get("type").value == "done":
        return Q(end_datetime__lt=timezone.datetime.now())


def final_filter_query(events_serializer, owner):
    return (
            Q(title__icontains=events_serializer.data.get("search_query"))
            & filter_from_datetime_query(events_serializer)
            & filter_until_datetime_query(events_serializer)
            & filter_owner_query(owner)
            & filter_participant_query(events_serializer)
            & filter_type_query(events_serializer)
    )


def final_filter_query_client(events_serializer):
    return (
            Q(title__icontains=events_serializer.data.get("search_query"))
            & filter_from_datetime_query(events_serializer)
            & filter_until_datetime_query(events_serializer)
            & filter_participant_query(events_serializer)
            & filter_type_query(events_serializer)
    )


def get_sorted_events(events_serializer, owner):
    return Event.objects.filter(final_filter_query(events_serializer, owner)).order_by(
        events_serializer.data.get("sort").value
    )


def get_sorted_events_client(events_serializer):
    return Event.objects.filter(final_filter_query_client(events_serializer)).order_by(
        events_serializer.data.get("sort").value
    )


def create_an_event(validated_data, owner):
    event = Event.objects.create(
        start_datetime=validated_data["start_datetime"],
        end_datetime=validated_data["end_datetime"],
        title=validated_data["title"],
        discount=validated_data["discount"],
        category=get_object_or_404(Category, id=validated_data["category_id"]),
        owner=owner,
        price=validated_data["price"]
    )
    return event


def get_event_history_client(client: UserProfile, page: int, page_count: int, request: Request):
    paginator = PageNumberPagination()
    paginator.page_size = page_count
    paginator.page = page
    events = Event.objects.filter(participants=client)
    return paginator.paginate_queryset(events, request)
