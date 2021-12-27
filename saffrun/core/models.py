from django.contrib.auth.models import User
from versatileimagefield.fields import VersatileImageField, PPOIField
from django.db import models

from profile.models import EmployeeProfile

from saffrun.category.models import Category


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Comment(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments"
    )
    text = models.TextField()


class Image(BaseModel):
    def get_file_path(self, filename):
        return "images/" + filename

    image = VersatileImageField(
        "Image",
        upload_to=get_file_path,
        ppoi_field="image_ppoi",
        null=True,
        blank=True,
    )
    image_ppoi = PPOIField(null=True, blank=True)


class Business(models.Model):
    owner = models.OneToOneField(EmployeeProfile, on_delete=models.CASCADE, related_name='business')
    title = models.CharField(max_length=150)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='businesses')
    establishment_date = models.DateTimeField()
    worker_count = models.IntegerField()
    email = models.EmailField()
    phone_number = models.CharField(max_length=12)
    full_address = models.TextField()
    description = models.TextField()
    images = models.ManyToManyField(Image, related_name="businesses", blank=True)

    def __str__(self):
        return self.title
