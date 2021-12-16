from django.db.models import Count
from django.db.models.functions import TruncMonth
from rest_flex_fields import FlexFieldsModelViewSet
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from datetime import datetime, timedelta
from .models import Image
from .serializers import ImageSerializer
from profile.models import EmployeeProfile, UserProfile

from event.models import Event
from reserve.models import Reservation


class ImageViewSet(FlexFieldsModelViewSet):
    serializer_class = ImageSerializer
    queryset = Image.objects.all()


class HomePage(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.profile = None

    def _get_profile(self):
        try:
            profile = EmployeeProfile.objects.get(user=self.request.user)
        except EmployeeProfile.DoesNotExist:
            profile = UserProfile.objects.get(user=self.request.user)
        if profile is None:
            raise Exception('No profile Found!')
        return profile


    def get(self, request, *args, **kwargs):
        self.profile = self._get_profile()
        return Response({'first_name': self.profile.user.first_name,
                         'last_name': self.profile.user.last_name,
                         'followers': self.profile.userprofile_set.count(),
                         'events_count': Event.objects.filter(owner=self.profile).count(),
                         'active_events_count': Event.objects.filter(owner=self.profile, end_datetime__gte=datetime.now()).count(),
                         'all_reserves_count': Reservation.objects.filter(owner=self.profile).count(),
                         'reserved_count': Reservation.objects.filter(owner=self.profile).values('participants').count(),
                         'montly': Reservation.objects.annotate(month=TruncMonth('end_datetime')).values('month').annotate(
                             total=Count('participants')).count(),
                         'monthly_all_reserves': Reservation.objects.annotate(month=TruncMonth('end_datetime')).values('month').count(),
                         })