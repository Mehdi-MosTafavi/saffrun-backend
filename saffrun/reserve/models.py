from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from core.models import BaseModel

from profile.models import UserProfile, EmployeeProfile


class ReservationManager(models.Manager):
    def get_queryset(self):
        return super(ReservationManager, self).get_queryset().filter(is_active=True)

class Reservation(BaseModel):
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    capacity = models.PositiveIntegerField()
    owner = models.ForeignKey(
        EmployeeProfile, on_delete=models.CASCADE, related_name="owned_reserves"
    )
    participants = models.ManyToManyField(
        UserProfile, related_name="participated_reserves", blank=True
    )
    objects = ReservationManager()
    price = models.IntegerField(default=0, null=False)
    def get_start_datetime(self):
        return self.start_datetime.replace(tzinfo=timezone.utc).astimezone(
            tz=None
        )

    def get_end_datetime(self):
        return self.end_datetime.replace(tzinfo=timezone.utc).astimezone(
            tz=None
        )
