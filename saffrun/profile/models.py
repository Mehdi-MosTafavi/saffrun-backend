# Create your models here.
from category.models import Category
from core.models import BaseModel
from core.models import Image
from django.contrib.auth.models import User
from django.db import models

GENDER_CHOICES = (
    ('M', 'male'),
    ('F', 'female'),
    ('N', 'not specified'),
)


class ProfileBase(BaseModel):
    phone = models.CharField(max_length=11, null=True, unique=True, blank=True)
    country = models.CharField(max_length=20, null=True, blank=True)
    city = models.CharField(max_length=20, null=True, blank=True)
    province = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=50, null=True, blank=True)
    gender = models.CharField(choices=GENDER_CHOICES, max_length=1, default='N')

    avatar = models.ForeignKey(
        Image,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )

    class Meta:
        abstract = True


class UserProfile(ProfileBase):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="user_profile"
    )
    following = models.ManyToManyField("EmployeeProfile", blank=True, related_name="followers")
    notification_token = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.user.username


class EmployeeProfile(ProfileBase):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="employee_profile"
    )

    class LevelChoice(models.IntegerChoices):
        VIP = 0, "VIP"
        NORMAL = 1, "NORMAL"

    level = models.IntegerField(
        choices=LevelChoice.choices, default=LevelChoice.NORMAL
    )
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True,
                                 related_name='category_employee')

    def __str__(self):
        return self.user.username
