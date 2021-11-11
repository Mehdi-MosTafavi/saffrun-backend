from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"upload", views.ImageViewSet)
urlpatterns = [
    path(r"image", include(router.urls)),
]
