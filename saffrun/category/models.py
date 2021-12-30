from django.db import models

# Create your models here.
from core.models import BaseModel


class Category(BaseModel):
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name