from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.create_reserves, name="create-reserves"),
    path("get-all/", views.get_all_reserves, name="get-all-reserves"),
]
