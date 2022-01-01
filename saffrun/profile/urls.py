from profile import views

from django.urls import path
from profile.views import UserView, FollowEmployee
from profile.views import remove_follower

app_name = "profile"
urlpatterns = [
    path("user/", UserView.as_view(), name="user_get"),
    path("follow/", FollowEmployee.as_view(), name="follow"),
    path("follow/remove-follower", remove_follower, name="follow-remove"),
    path(r"web/business/", views.BusinessView.as_view(), name="web-business"),
    path(r"client/business/<int:employee_id>", views.GetBusinessClientView.as_view(), name="client-business")
]
