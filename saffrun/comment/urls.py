from django.urls import path
from . import views

app_name = "comment"
urlpatterns = [
    path("save_comment/", views.save_comment, name="save_comment"),
    path("save_reply/", views.save_reply, name="save_reply"),
    path("get_event_comments/", views.get_all_event_comments, name="get_all_event_comments"),
    path("get_owner_comments/", views.get_all_owner_comments, name="get_all_owner_comments"),
    path("get_comment_of_owner/", views.get_comment_of_owner, name="get_all_owner_comments"),

]