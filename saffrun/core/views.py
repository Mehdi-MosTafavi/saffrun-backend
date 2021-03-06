from comment.models import Comment
from django.db.models import Count
from django.db.models import F
from django.db.models.functions import TruncMonth
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from event.models import Event
from profile.models import EmployeeProfile, UserProfile
from profile.serializers import EventReserveSerializer
from reserve.models import Reservation
from rest_flex_fields import FlexFieldsModelViewSet
from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Image
from .responses import ErrorResponse
from .serializers import ImageSerializer, HomepageResponse, HomepageResponseClient, GetYearlyDetailSerializer, \
    ClientSearchSerializer, EventBusinessSerializer
from .services import is_user_employee, is_user_client
from .utils import get_event_businesses_list
from .utils import get_yearly_details, get_offers


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
            data={
                'image': ImageSerializer(self.profile.avatar).data,
                'first_name': self.profile.user.first_name,
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
                                                                                    'end_datetime',
                                                                                    'participant_count',
                                                                                    province=F('owner__province')),
                'number_of_comments': Comment.objects.filter(owner=self.profile).count(),
                'number_of_user_comments': Comment.objects.filter(owner=self.profile, is_parent=True).values(
                    'user').distinct().count(),
                'rate': self.profile.business.rate,
                'number_user_rate': self.profile.business.rate_count,
                'last_comments': Comment.objects.filter(owner=self.profile, is_parent=True).order_by(
                    '-id').annotate(
                    username=F('user__user__username')).values('username',
                                                               'content',
                                                               'created_at')[:3],
                'number_of_all_reserves': Reservation.objects.filter(owner=self.profile).count(),
                'number_of_given_reserves': Reservation.objects.filter(
                    owner=self.profile, participants__isnull=False).count(),
                'last_given_reserves': self.get_reserve_of_user(),
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

    def get_reserve_of_user(self):
        reserves = Reservation.objects.filter(owner=self.profile,
                                              participants__isnull=False).order_by(
            '-updated_at').distinct()
        reserves_list = []
        for reserve in reserves:
            list_participants = []
            for user in reserve.participants.all():
                list_participants.append({
                    'first_name': user.user.first_name,
                    'last_name': user.user.last_name,
                    'image': ImageSerializer(instance=user.avatar).data
                })
            reserves_list.append({
                'start_datetime': reserve.get_start_datetime(),
                'end_datetime': reserve.get_end_datetime(),
                'province': reserve.owner.province,
                'list_participants': list_participants
            })
        return reserves_list[:5]


class HomePageClient(generics.RetrieveAPIView):
    permission_classes = (AllowAny,)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.profile = None

    def _get_profile(self):
        try:
            profile = EmployeeProfile.objects.get(user=self.request.user)
        except:
            try:
                profile = UserProfile.objects.get(user=self.request.user)
            except:
                return None
        if profile is None:
            return None
        return profile

    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: HomepageResponseClient,
            status.HTTP_500_INTERNAL_SERVER_ERROR: ErrorResponse.INVALID_DATA
        }
    )
    def get(self, request, *args, **kwargs):
        self.profile = self._get_profile()
        if self.profile is None:
            return Response(
                exception={"error": ErrorResponse.INVALID_DATA},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        time = timezone.now()
        serializer = HomepageResponseClient(
            data={
                'list_event': Event.objects.filter(
                    participants__in=[self.profile.id],
                    end_datetime__gte=time
                ).order_by('-updated_at').distinct().values('id', 'title', 'description', 'start_datetime',
                                                            'end_datetime', owner_name=F('owner__business__title')),
                'list_reserve': [dict(item, **{'picture': ImageSerializer(
                    instance=get_object_or_404(Image, avatar_employee=item['ownerId'])).data}) for item in
                                 Reservation.objects.filter(
                                     participants__in=[self.profile.id],
                                     end_datetime__gte=time
                                 ).order_by('-updated_at').distinct().values('id', 'start_datetime', 'end_datetime',
                                                                             ownerId=F('owner__id'),
                                                                             owner_name=F('owner__business__title'),
                                                                             )],

            }
        )

        if serializer.is_valid():
            return Response(serializer.data)
        print(serializer.errors)
        return Response(
            exception={"error": ErrorResponse.INVALID_DATA,
                       "validation_errors": serializer.errors},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


class GetYearlyDetails(APIView):
    @swagger_auto_schema(
        query_serializer=GetYearlyDetailSerializer,
        responses={
            status.HTTP_200_OK: EventReserveSerializer,
            status.HTTP_400_BAD_REQUEST: ErrorResponse.USER_EMPLOYEE,
            status.HTTP_406_NOT_ACCEPTABLE: ErrorResponse.INVALID_DATA
        }
    )
    def get(self, request):
        year_serializer = GetYearlyDetailSerializer(data=request.GET)
        if not year_serializer.is_valid():
            return Response(
                exception={"error": ErrorResponse.INVALID_DATA},
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )
        if not is_user_employee(request.user):
            return Response(
                {"status": "Error", "detail": ErrorResponse.USER_EMPLOYEE},
                status=400,
            )
        event_reserve_result = get_yearly_details(request.user.employee_profile,
                                                  year_serializer.validated_data.get("year"))
        return Response({"result": event_reserve_result}, status=200)

class ClientSearchView(APIView):
    @swagger_auto_schema(
        query_serializer=ClientSearchSerializer,
        responses={
            status.HTTP_200_OK: EventBusinessSerializer,
            status.HTTP_400_BAD_REQUEST: ErrorResponse.USER_CLIENT,
            status.HTTP_406_NOT_ACCEPTABLE: ErrorResponse.INVALID_DATA
        }
    )
    def get(self, request):
        serializer = ClientSearchSerializer(data=request.GET)
        if not serializer.is_valid():
            return Response(
                exception={"error": ErrorResponse.INVALID_DATA},
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )
        if not is_user_client(request.user):
            return Response(
                {"status": "Error", "detail": ErrorResponse.USER_CLIENT},
                status=400,
            )
        search_query = serializer.validated_data.get('search_query')
        category_id = serializer.validated_data.get('category')
        sort = serializer.validated_data.get('sort')
        from_datetime = serializer.validated_data.get('from_datetime')
        until_datetime = serializer.validated_data.get('until_datetime')

        events_businesses_dict = get_event_businesses_list(
            search_query, category_id, sort, from_datetime, until_datetime
        )

        return Response(events_businesses_dict, status=200)

class ClientOfferView(APIView):
    @swagger_auto_schema(
        responses={
            status.HTTP_200_OK: EventBusinessSerializer,
            status.HTTP_400_BAD_REQUEST: ErrorResponse.USER_CLIENT,
        }
    )
    def get(self, request):
        if not is_user_client(request.user):
            return Response(
                {"status": "Error", "detail": ErrorResponse.USER_CLIENT},
                status=400,
            )

        offers = get_offers(request.user.user_profile)
        return Response(offers, status=200)

