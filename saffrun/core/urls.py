from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = "core"
router = DefaultRouter()
router.register(r"upload", views.ImageViewSet)
urlpatterns = [
    path(r"image/", include(router.urls)),
    path(r"homepage/", views.HomePage.as_view(), name="homepage"),
    path(r"client/homepage/", views.HomePageClient.as_view(), name="homepage-client"),
    path(r"web/business/", views.BusinessView.as_view(), name="web-business"),
    path(r"client/business/<int:employee_id>", views.GetBusinessClientView.as_view(), name="client-business"),
    path(r"web/get-yearly-details/", views.GetYearlyDetails.as_view(), name="get-yearly-details"),
    path(r"business/rate/", views.RateBusiness.as_view(), name="rate-business")
]
