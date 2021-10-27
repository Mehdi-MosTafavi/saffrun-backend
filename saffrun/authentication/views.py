# Create your views here.
from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from rest_framework import generics

from authentication.serializers import RegisterSerializer


class RegisterUser(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer
