from django.urls import path

from . import views
from .views import RetrieveEventAPIView, remove_participant

app_name = "event"
urlpatterns = [
    path(
        "<int:pk>",
        views.EventRetrieveUpdateDestroyAPIView.as_view(),
        name="event",
    ),
    path("get-detail-event/<int:pk>", RetrieveEventAPIView.as_view(), name="get-detail-event"),
    path("add/", views.create_event, name="add-event"),
    path("get-all/", views.get_all_events, name="get-all-events"),
    path(
        "add-participants/",
        views.add_participants_to_event,
        name="add-participants",
    ),
    path(
        "add-image/",
        views.add_image_to_event,
        name="add-image",
    ),
    path(
        'get-client-reserve-history',
        views.ClientEventHistory.as_view(),
        name='client-reserve-history'
    ),
    path(
        'remove-participant-event',
        remove_participant,
        name='remove-particpant-event'
    )
]
