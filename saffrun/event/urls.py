from django.urls import path
from . import views

urlpatterns = [path("get/<int:event_id>", views.get_event, name="get-event")]
