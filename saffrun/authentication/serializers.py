from django.contrib.auth.models import User, AbstractUser
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "username",
            "password",
        ]

    extra_kwargs = {
        "password": {"write_only": True, "min_length": 8},
    }

    def create_instance(self):
        new_user = User.objects.create(username=self.validated_data["username"])
        new_user.set_password(self.validated_data['password'])
        return new_user


class ShortUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username"]

class ChangePasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "password",
        ]