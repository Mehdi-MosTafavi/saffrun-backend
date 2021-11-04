from django.contrib.auth.models import User
from django.db import models

from saffrun.commons.BaseModel import BaseModel


class Reservation(BaseModel):
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    capacity = models.PositiveIntegerField()
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="owned_reserves"
    )
    participants = models.ManyToManyField(
        User, related_name="participated_reserves"
    )
