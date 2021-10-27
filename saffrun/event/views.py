from rest_framework.decorators import api_view
from rest_framework.generics import RetrieveUpdateDestroyAPIView, CreateAPIView
from .models import Event
from .serializers import EventSerializer


class EventRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


class CreateEvent(CreateAPIView):
    queryset = Event.objects.all()
    serializer_class = EventSerializer


@api_view(["GET"])
def get_all_event(request):
    pass
