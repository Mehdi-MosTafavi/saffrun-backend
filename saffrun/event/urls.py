from django.urls import path
from . import views

urlpatterns = [
    path("get/", views.get_event, name="get-event"),
    path("add/", views.add_event, name="add-event"),
]
