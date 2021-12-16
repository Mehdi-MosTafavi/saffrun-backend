from rest_framework import serializers


class AddNotificationTokenSerializer(serializers.Serializer):
    notification_token = serializers.CharField(max_length=200)