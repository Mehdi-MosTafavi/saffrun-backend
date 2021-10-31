from .models import Image
from versatileimagefield.serializers import VersatileImageFieldSerializer
from rest_flex_fields import FlexFieldsModelSerializer


class ImageSerializer(FlexFieldsModelSerializer):
    image = VersatileImageFieldSerializer(
        sizes=[
            ("full_size", "url"),
            ("thumbnail", "thumbnail__100x100"),
        ]
    )

    class Meta:
        ref_name = "image_serializer"
        model = Image
        fields = ["id", "image"]
