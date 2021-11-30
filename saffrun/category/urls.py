from django.urls import path
from . import views

app_name = "category"
urlpatterns = [
    path("get-all/", views.CategoryGetAll.as_view(), name="get-all-categories"),
]