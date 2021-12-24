from core.responses import ErrorResponse, SuccessResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView, CreateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Event
from .serializers import (
    EventSerializer,
    AllEventSerializer,
    ManyEventSerializer,
    AddParticipantSerializer,
    AddImageSerializer,
    EventImageSerializer, EventHistorySerializer,
)
from .utils import get_sorted_events, create_an_event, get_event_history_client
from core.services import is_user_employee

from core.serializers import GetAllSerializer

from core.services import is_user_client


class EventRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventImageSerializer


@swagger_auto_schema(
    method="post",
    request_body=EventSerializer,
    responses={
        201: SuccessResponse.CREATED,
        400: ErrorResponse.USER_EMPLOYEE,
        406: ErrorResponse.INVALID_DATA,
    },
)
@api_view(["POST"])
def create_event(request):
    event_serializer = EventSerializer(data=request.data)
    if not event_serializer.is_valid():
        return Response(
            {"Error": ErrorResponse.INVALID_DATA},
            status=status.HTTP_406_NOT_ACCEPTABLE,
        )

    if not is_user_employee(request.user):
        return Response(
            {"status": "Error", "detail": ErrorResponse.USER_EMPLOYEE},
            status=400,
        )

    event: Event = create_an_event(
        event_serializer.validated_data, request.user.employee_profile
    )
    return Response(
        {"event_id": event.id , "success": SuccessResponse.CREATED}, status=status.HTTP_201_CREATED
    )


@swagger_auto_schema(
    method="get",
    query_serializer=AllEventSerializer,
    responses={200: ManyEventSerializer, 406: ErrorResponse.INVALID_DATA, 400:ErrorResponse.USER_EMPLOYEE},
)
@api_view(["GET"])
def get_all_events(request):
    """
    Getting all the event
    You have to provide search_query(could be blank but not null) and a sort field
    sort 1 = by title (default)
    sort 2 = by start_date
    participant_id, from_datetime, until_datetime are optional field
    """
    events_serializer = AllEventSerializer(data=request.GET)
    if not events_serializer.is_valid():
        return Response(
            {"Error": ErrorResponse.INVALID_DATA},
            status=status.HTTP_406_NOT_ACCEPTABLE,
        )
    if is_user_employee(request.user):
        events = get_sorted_events(events_serializer, request.user.employee_profile)
        paginator = PageNumberPagination()
        paginator.page_size = events_serializer.validated_data["page_count"]
        paginator.page = events_serializer.validated_data["page"]
        events = paginator.paginate_queryset(events, request)
        return Response(
            {"events": EventImageSerializer(instance=events, many=True).data},
            status=status.HTTP_200_OK,
        )
    else:
        return Response(
            {"status": "Error", "detail": ErrorResponse.USER_EMPLOYEE},
            status=400,
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

class ClientEventHistory(APIView):
    @swagger_auto_schema(
        query_serializer=GetAllSerializer,
        responses={
            status.HTTP_200_OK: EventHistorySerializer,
            status.HTTP_400_BAD_REQUEST: ErrorResponse.USER_CLIENT,
            status.HTTP_406_NOT_ACCEPTABLE: ErrorResponse.INVALID_DATA,
        }
    )
    def get(self, request):
        events_serializer = GetAllSerializer(data=request.GET)
        if not events_serializer.is_valid():
            return Response(
                exception={"error": ErrorResponse.INVALID_DATA},
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )
        if not is_user_client(request.user):
            return Response(
                {"status": "Error", "detail": ErrorResponse.USER_CLIENT},
                status=status.HTTP_400_BAD_REQUEST,
            )
        page = events_serializer.validated_data.get("page")
        page_count = events_serializer.validated_data.get("page_count")
        events = get_event_history_client(request.user.user_profile, page, page_count, request)
        return Response({"reserves": EventHistorySerializer(events, many=True).data}, status=200)

