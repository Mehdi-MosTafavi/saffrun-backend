from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from saffrun.commons.BaseModel import BaseModel


class ProfileBase(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=11, null=True, unique=True)
    country = models.CharField(max_length=20, null=True)
    province = models.CharField(max_length=20, null=True)
    address = models.CharField(max_length=50, null=True)
    avatar = models.URLField(null=True)

    class Meta:
        abstract = True


class UserProfile(ProfileBase):
    pass


class Employee(ProfileBase):
    class LevelChoice(models.IntegerChoices):
        VIP = 0, 'VIP'
        NORMAL = 1, 'NORMAL'

    level = models.IntegerField(choices=LevelChoice.choices, default=LevelChoice.NORMAL)
