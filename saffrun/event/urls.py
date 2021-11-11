from django.urls import path
from . import views

app_name = "event"
urlpatterns = [
    path(
        "<int:pk>",
        views.EventRetrieveUpdateDestroyAPIView.as_view(),
        name="event",
    ),
    path("add/", views.CreateEvent.as_view(), name="add-event"),
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
]
