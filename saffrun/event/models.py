from django.contrib.auth.models import User
from django.db import models
from saffrun.commons.BaseModel import BaseModel

# Create your models here.
from comment.models import Comment


class Event(BaseModel):
    title = models.CharField(max_length=200)
    participants = models.ManyToManyField(
        User, related_name="participated_events", blank=True
    )
    description = models.TextField(blank=True, null=True)
    image = models.OneToOneField(
        "image.Image",
        related_name="event",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    discount = models.PositiveIntegerField()
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="owned_event"
    )
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
