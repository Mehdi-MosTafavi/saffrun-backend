from django.urls import path
from . import views

urlpatterns = [
    path(
        "<int:pk>",
        views.EventRetrieveUpdateDestroyAPIView.as_view(),
        name="event",
    ),
    path("add/", views.CreateEvent.as_view(), name="add-event"),
]
