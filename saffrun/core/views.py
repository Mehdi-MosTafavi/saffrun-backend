from rest_flex_fields import FlexFieldsModelViewSet

from .models import Image
from .serializers import ImageSerializer


class ImageViewSet(FlexFieldsModelViewSet):
    serializer_class = ImageSerializer
    queryset = Image.objects.all()
