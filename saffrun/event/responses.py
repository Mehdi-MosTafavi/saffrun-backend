from drf_yasg import openapi

from .serializers import EventSerializer

event_response = openapi.Response("Instance of event", EventSerializer)
