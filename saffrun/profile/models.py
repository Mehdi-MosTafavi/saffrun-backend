from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from core.models import BaseModel


class ProfileBase(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=11, null=True, unique=True, blank=True)
    country = models.CharField(max_length=20, null=True, blank=True)
    province = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=50, null=True, blank=True)
    avatar = models.URLField(null=True, blank=True)

    class Meta:
        abstract = True


class UserProfile(ProfileBase):
    following = models.ManyToManyField('EmployeeProfile', blank=True)

    def __str__(self):
        return self.user.username


class EmployeeProfile(ProfileBase):
    class LevelChoice(models.IntegerChoices):
        VIP = 0, 'VIP'
        NORMAL = 1, 'NORMAL'

    level = models.IntegerField(choices=LevelChoice.choices, default=LevelChoice.NORMAL)

    def __str__(self):
        return self.user.username
