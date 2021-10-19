from django.urls import path

from authentication.views import RegisterUser

app_name = 'auth'
urlpatterns = [
    path('register/', RegisterUser.as_view())
]