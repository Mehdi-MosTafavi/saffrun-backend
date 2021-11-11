from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.create_reserves, name="create-reserves"),
    path("get-all-reserves/", views.get_all_reserves, name="get-all-reserves"),
    path("get-busy-dates/", views.get_user_busy_dates, name="user-busy-dates"),
]
