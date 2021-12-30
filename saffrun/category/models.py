from django.contrib.auth.models import User
from django.db import models
from django.db import models

# Create your models here.
from core.models import BaseModel, Image


class Category(BaseModel):
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name