from django.urls import path
from . import views

urlpatterns = [path("create/", views.create_reserves, name="create-reserves")]
