from django.urls import path
from . import views

app_name = "notification"
urlpatterns = [
    path(
        "set-user-notification-token/",
        views.SetUserNotificationToken.as_view(),
        name="set-user-notification-token",
    ),
    path(
        "send-notification/",
        views.SendNotification.as_view(),
        name="send-notification",
    ),
]
