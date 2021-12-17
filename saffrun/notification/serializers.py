from rest_framework import serializers

from .models import Notification


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
        fields = ["title", "text", "type", "url", "receivers_count"]

class ClientGetNotificationSerializer(serializers.ModelSerializer):
    sender = serializers.StringRelatedField()

    class Meta:
        model = Notification
        fields = ["title", "text", "type", "url", "sender"]

class GetNotificationsSerializer(serializers.Serializer):
    page = serializers.IntegerField()
    page_count = serializers.IntegerField()