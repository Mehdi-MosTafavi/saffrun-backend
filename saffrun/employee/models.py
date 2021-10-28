from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from saffrun.commons.BaseModel import BaseModel


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
