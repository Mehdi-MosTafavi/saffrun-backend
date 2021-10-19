from django.contrib.auth.models import User
from rest_framework import serializers


class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField()

    class Meta:
        model = User
        fields = [
            'username',
            'password',
            'confirm_password',
        ]

    extra_kwargs = {
        'password': {'write_only': True, 'min_length': 8},
        'confirm_password': {'write_only': True, 'min_length': 8},
    }

    def validate_password(self, password: str) -> str:
        data = dict(self.initial_data)
        if password != data.pop('confirm_password'):
            raise serializers.ValidationError("Passwords does not match.")
        return password

    def create(self, validated_data):
        print(validated_data)
        new_user = User.objects.create(username=validated_data['username'])
        new_user.set_password(validated_data['password'])
        new_user.save()
        return new_user
