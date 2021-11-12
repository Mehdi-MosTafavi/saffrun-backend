from django.urls import path
from profile.views import UserView, FollowEmployee

app_name = "profile"
urlpatterns = [
    path("user/", UserView.as_view(), name="user_get"),
    path("follow/", FollowEmployee.as_view(), name="follow")
]
