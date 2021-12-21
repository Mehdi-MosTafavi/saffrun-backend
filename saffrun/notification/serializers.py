from rest_framework import serializers

from .models import Notification
from profile.serializers import EmployeeProfileSerializer


class AddNotificationTokenSerializer(serializers.Serializer):
    notification_token = serializers.CharField(max_length=200)

class SendNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["title", "text", "type", "url"]

class EmployeeGetNotificationsSerializer(serializers.ModelSerializer):
    receivers_count = serializers.SerializerMethodField('get_receivers_count')

    @staticmethod
    def get_receivers_count(notification):
        return notification.receivers.all().count()

    class Meta:
        model = Notification
        fields = ["title", "text", "type", "url", "receivers_count", "created_at"]


class ClientGetNotificationSerializer(serializers.ModelSerializer):
    sender = EmployeeProfileSerializer()

    class Meta:
        model = Notification
        fields = ["title", "text", "type", "url", "sender", "created_at"]

class GetNotificationsSerializer(serializers.Serializer):
    page = serializers.IntegerField()
    page_count = serializers.IntegerField()