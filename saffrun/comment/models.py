from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from saffrun.commons.BaseModel import BaseModel


class Comment(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments"
    )
    text = models.TextField()
