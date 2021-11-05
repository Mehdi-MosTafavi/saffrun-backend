from django.urls import path
from profile.views import UserView
app_name = "profile"
urlpatterns = [
    path("user/", UserView.as_view(), name="user_get"),
]
