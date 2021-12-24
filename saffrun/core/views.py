from django.db.models import Count
from django.db.models.functions import TruncMonth
from drf_yasg.utils import swagger_auto_schema
from rest_flex_fields import FlexFieldsModelViewSet
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import F
from .models import Image
from django.utils import timezone
from .responses import ErrorResponse
from .serializers import ImageSerializer, HomepageResponse
from profile.models import EmployeeProfile, UserProfile
from comment.models import Comment
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

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: HomepageResponse,
            status.HTTP_500_INTERNAL_SERVER_ERROR: ErrorResponse.INVALID_DATA
        }
    )
    def get(self, request, *args, **kwargs):
        self.profile = self._get_profile()
        serializer = HomepageResponse(
            data={'first_name': self.profile.user.first_name,
                  'last_name': self.profile.user.last_name,
                  'followers': self.profile.followers.count(),
                  'number_of_events': Event.objects.filter(owner=self.profile).count(),
                  'number_of_active_events': Event.objects.filter(owner=self.profile,
                                                                  end_datetime__gte=timezone.now()).count(),
                  'monthly_events': Event.objects.filter(owner=self.profile).annotate(
                      month=TruncMonth('end_datetime'),
                      total=Count(
                          'participants')).values('month', 'total').order_by(
                      'month').distinct(),
                  'last_events': Event.objects.filter(owner=self.profile).order_by(
                      '-id').annotate(participant_count=Count('participants')).values('title',
                                                                                      'start_datetime',
                                                                                      'participant_count'),
                  'number_of_comments': Comment.objects.filter(owner=self.profile).count(),
                  'last_comments': Comment.objects.filter(owner=self.profile).order_by(
                      '-id').annotate(
                      username=F('user__user__username')).values('username',
                                                                 'content',
                                                                 'created_at')[:3],
                  'number_of_all_reserves': Reservation.objects.filter(owner=self.profile).count(),
                  'number_of_given_reserves': Reservation.objects.filter(
                      owner=self.profile, participants__isnull=False).count(),
                  'last_given_reserves': Reservation.objects.filter(owner=self.profile,
                                                                    participants__isnull=False).order_by(
                      '-updated_at').annotate(first_name=F('participants__user__first_name'),
                                              last_name=F(
                                                  'participants__user__last_name')).values(
                      'first_name',
                      'last_name',
                      'start_datetime')[:5],
                  'monthly_reserves': Reservation.objects.annotate(
                      month=TruncMonth('end_datetime'), total=Count('participants')).values(
                      'month', 'total').order_by('month').distinct(),
                  })
        if serializer.is_valid():
            return Response(serializer.data)
        return Response(
            exception={"error": ErrorResponse.INVALID_DATA,
                       "validation_errors": serializer.errors},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
