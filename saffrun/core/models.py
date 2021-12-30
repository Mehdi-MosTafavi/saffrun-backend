from django.db import models

from profile.models import EmployeeProfile

from saffrun.category.models import Category


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True

from versatileimagefield.fields import VersatileImageField, PPOIField

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


from profile.models import EmployeeProfile
from category.models import Category

class Business(models.Model):
    owner = models.OneToOneField(EmployeeProfile, on_delete=models.CASCADE, related_name='business')
    title = models.CharField(max_length=150, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='businesses', null=True)
    establishment_date = models.DateTimeField(null=True)
    worker_count = models.IntegerField(null=True)
    email = models.EmailField(null=True)
    phone_number = models.CharField(max_length=12, null=True)
    full_address = models.TextField(null=True)
    description = models.TextField(null=True)
    images = models.ManyToManyField(Image, related_name="businesses", blank=True, null=True)
    rate = models.FloatField(null=True)
    rate_count = models.IntegerField(null=True)
