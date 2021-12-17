from django.db import models

# Create your models here.
from core.models import BaseModel

from profile.models import UserProfile, EmployeeProfile


class Notification(BaseModel):
    class NotificationType(models.IntegerChoices):
        FOLLOWERS = 1
        EVERYONE = 2
    title = models.CharField(max_length=150, null=False, blank=False)
    text = models.CharField(max_length=500, null=False, blank=False)
    sender = models.ForeignKey(EmployeeProfile, related_name='sent_notifications', on_delete=models.CASCADE)
    receivers = models.ManyToManyField(UserProfile, related_name="received_notifications")
    type = models.IntegerField(choices=NotificationType.choices, default=NotificationType.FOLLOWERS)
    url = models.CharField(max_length=300, null=False, blank=True)

    def __str__(self):
        return self.title + ": " + self.text