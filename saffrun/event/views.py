from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import RetrieveUpdateDestroyAPIView, CreateAPIView
from rest_framework.response import Response

from .const import INVALID_DATA
from .models import Event
from .serializers import (
    EventSerializer,
    AllEventSerializer,
    ManyEventSerializer,
)


class EventRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


class CreateEvent(CreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


@swagger_auto_schema(
    method="get",
    query_serializer=AllEventSerializer,
    responses={200: ManyEventSerializer, 406: INVALID_DATA},
)
@api_view(["GET"])
def get_all_events(request):
    """
    Getting all the event
    You have to provide search_query(could be blank but not null) and a sort field
    sort 1 = by title (default)
    sort 2 = by start_date
    participant_id, owner_id, from_datetime, until_datetime are optional field
    """
    events_serializer = AllEventSerializer(data=request.GET)
    if not events_serializer.is_valid():
        return Response(
            {"Error": INVALID_DATA}, status=status.HTTP_406_NOT_ACCEPTABLE
        )
    from_datetime_query = (
        Q(start_datetime__gte=events_serializer.data.get("from_datetime"))
        if events_serializer.data.get("from_datetime")
        else Q()
    )
    until_datetime_query = (
        Q(end_datetime__lte=events_serializer.data.get("until_datetime"))
        if events_serializer.data.get("until_datetime")
        else Q()
    )
    owner_query = (
        Q(owner=events_serializer.data.get("owner_id"))
        if events_serializer.data.get("owner_id")
        else Q()
    )
    participant_query = (
        Q(participants__in=[events_serializer.data.get("participant_id")])
        if events_serializer.data.get("participant_id")
        else Q()
    )
    final_query = (
        Q(title__icontains=events_serializer.data.get("search_query"))
        & from_datetime_query
        & until_datetime_query
        & owner_query
        & participant_query
    )
    if events_serializer.data.get("sort") == 1:
        events = Event.objects.filter(final_query).order_by("title")
    else:
        events = Event.objects.filter(final_query).order_by("start_datetime")
    return Response(
        {"events": EventSerializer(instance=events, many=True).data},
        status=status.HTTP_200_OK,
    )
