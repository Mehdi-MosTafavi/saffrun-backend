from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .const import INVALID_DATA, NOT_FOUND
from .models import Event
from .parameters import event_id_param
from .responses import event_response
from .serializers import EventSerializer, GetEventSerializer


@swagger_auto_schema(
    method="get",
    manual_parameters=[event_id_param],
    responses={200: event_response, 406: INVALID_DATA, 404: NOT_FOUND},
)
@login_required
@api_view(["GET"])
def get_event(request):
    request_serializer = GetEventSerializer(data=request.GET)
    if not request_serializer.is_valid():
        return Response(
            {"error": INVALID_DATA}, status=status.HTTP_406_NOT_ACCEPTABLE
        )
    try:
        event = Event.objects.get(id=request_serializer.data["event_id"])
    except ObjectDoesNotExist:
        return Response({"error": NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
    serializer = EventSerializer(event)
    return Response(data=serializer.data, status=status.HTTP_200_OK)
