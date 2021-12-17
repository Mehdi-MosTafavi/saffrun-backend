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
    path(
        "employee/get-notifications/",
        views.EmployeeGetNotifications.as_view(),
        name="employee-get-notifications",
    ),
    path(
        "client/get-notifications/",
        views.ClientGetNotifications.as_view(),
        name="client-get-notifications",
    ),

]
