from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from saffrun.commons.BaseModel import BaseModel


class Reservation(BaseModel):
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    capacity = models.PositiveIntegerField()
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="owned_reserves"
    )
    participants = models.ManyToManyField(
        User, related_name="participated_reserves", null=True, blank=True
    )

    def get_start_datetime(self):
        return self.start_datetime.replace(tzinfo=timezone.utc).astimezone(
            tz=None
        )

    def get_end_datetime(self):
        return self.end_datetime.replace(tzinfo=timezone.utc).astimezone(
            tz=None
        )
