# Create your models here.
from category.models import Category
from core.models import BaseModel
from django.db import models
from django.utils import timezone
from profile.models import UserProfile, EmployeeProfile


class Event(BaseModel):
    title = models.CharField(max_length=200)
    participants = models.ManyToManyField(
        UserProfile, related_name="participated_events", blank=True
    )
    description = models.TextField(blank=True, null=True)
    images = models.ManyToManyField(
        "core.Image",
        related_name="events",
        blank=True,
    )
    discount = models.PositiveIntegerField()
    owner = models.ForeignKey(
        EmployeeProfile, on_delete=models.CASCADE, related_name="owned_event"
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='category_event')
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    def get_start_datetime(self):
        return self.start_datetime.replace(tzinfo=timezone.utc).astimezone(
            tz=None
        )

    def get_end_datetime(self):
        return self.end_datetime.replace(tzinfo=timezone.utc).astimezone(
            tz=None
        )
