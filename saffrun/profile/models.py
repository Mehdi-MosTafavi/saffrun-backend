from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from saffrun.commons.BaseModel import BaseModel


class ProfileBase(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class Employee(ProfileBase):
    pass
