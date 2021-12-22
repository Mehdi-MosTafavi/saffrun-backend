from django.urls import path
from profile.views import UserView, FollowEmployee

from profile.views import remove_follower

app_name = "profile"
urlpatterns = [
    path("user/", UserView.as_view(), name="user_get"),
    path("follow/", FollowEmployee.as_view(), name="follow"),
    path("follow/remove-follower", remove_follower, name="follow-remove"),
]
