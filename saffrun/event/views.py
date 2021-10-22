from django.contrib.auth.decorators import login_required
from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Event
from .serializers import EventSerializer


@api_view(["GET"])
def get_event(request, event_id):
    event = Event.objects.get(id=event_id)
    serializer = EventSerializer(event)
    return Response(data=serializer.data)
