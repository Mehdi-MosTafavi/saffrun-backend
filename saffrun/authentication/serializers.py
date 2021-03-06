from django.contrib.auth.models import User
from django.db import models
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    class ClientChoices(models.TextChoices):
        APP = "app"
        WEB = "web"

    client = serializers.ChoiceField(ClientChoices, allow_blank=False, allow_null=False)

    class Meta:
        model = User
        fields = [
            "username",
            "password",
            "client"
        ]

    extra_kwargs = {
        "password": {"write_only": True, "min_length": 8},
    }

    def create_instance(self):
        new_user = User.objects.create(username=self.validated_data["username"])
        new_user.set_password(self.validated_data["password"])
        return new_user


class ShortUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]


class RecoverPasswordSerializer(serializers.Serializer):
    username = serializers.CharField()

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()
