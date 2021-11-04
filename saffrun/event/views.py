from django.db.models import Q
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import RetrieveUpdateDestroyAPIView, CreateAPIView
from rest_framework.response import Response

from saffrun.commons.ErrorResponse import ErrorResponse
from .models import Event
from .serializers import (
    EventSerializer,
    AllEventSerializer,
    ManyEventSerializer,
    AddParticipantSerializer,
    AddImageSerializer,
)
from .utils import get_sorted_events


class EventRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


class CreateEvent(CreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


@swagger_auto_schema(
    method="get",
    query_serializer=AllEventSerializer,
    responses={200: ManyEventSerializer, 406: ErrorResponse.INVALID_DATA},
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
            {"Error": ErrorResponse.INVALID_DATA},
            status=status.HTTP_406_NOT_ACCEPTABLE,
        )

    events = get_sorted_events(events_serializer)

    return Response(
        {"events": EventSerializer(instance=events, many=True).data},
        status=status.HTTP_200_OK,
    )


@swagger_auto_schema(
    method="post",
    request_body=AddParticipantSerializer,
    responses={
        200: EventSerializer,
        406: ErrorResponse.INVALID_DATA,
        404: ErrorResponse.NOT_FOUND,
    },
)
@api_view(["POST"])
def add_participants_to_event(request):
    add_serializer = AddParticipantSerializer(data=request.data)
    if not add_serializer.is_valid():
        return Response(
            {"Error": ErrorResponse.INVALID_DATA},
            status=status.HTTP_406_NOT_ACCEPTABLE,
        )
    return add_serializer.add_participants()


@swagger_auto_schema(
    method="post",
    request_body=AddImageSerializer,
    responses={
        200: EventSerializer,
        406: ErrorResponse.INVALID_DATA,
        404: ErrorResponse.NOT_FOUND,
    },
)
@api_view(["POST"])
def add_image_to_event(request):
    add_image_serializer = AddImageSerializer(data=request.data)
    if not add_image_serializer.is_valid():
        return Response(
            {"Error": ErrorResponse.INVALID_DATA},
            status=status.HTTP_406_NOT_ACCEPTABLE,
        )
    return add_image_serializer.add_image()
