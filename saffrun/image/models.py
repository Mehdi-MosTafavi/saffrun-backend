from django.db import models

from versatileimagefield.fields import VersatileImageField, PPOIField


class Image(models.Model):
    def get_file_path(self, filename):
        return "images/" + filename

    image = VersatileImageField(
        "Image", upload_to=get_file_path, ppoi_field="image_ppoi"
    )
    image_ppoi = PPOIField()
