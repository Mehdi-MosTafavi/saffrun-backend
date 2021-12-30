from versatileimagefield.fields import VersatileImageField, PPOIField
from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    class Meta:
        abstract = True

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
