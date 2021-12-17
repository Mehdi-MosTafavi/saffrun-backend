from rest_framework import serializers

from .models import Notification


class AddNotificationTokenSerializer(serializers.Serializer):
    notification_token = serializers.CharField(max_length=200)

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["title", "text", "type"]