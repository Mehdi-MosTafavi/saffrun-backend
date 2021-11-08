from django.shortcuts import render

# Create your views here.
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from saffrun.commons.responses import SuccessResponse, ErrorResponse

from .models import Reservation
from .serializers import (
    CreateReservesSerializer,
    GetAllReservesSerializer,
    AbstractReserveSerializer,
    ReserveFeatureSeriallizer,
)


@swagger_auto_schema(
    method="post",
    request_body=CreateReservesSerializer,
    responses={
        status.HTTP_201_CREATED: SuccessResponse.CREATED,
        status.HTTP_406_NOT_ACCEPTABLE: ErrorResponse.INVALID_DATA,
        status.HTTP_409_CONFLICT: ErrorResponse.COLLISION_Messaage,
    },
)
@api_view(["POST"])
def create_reserves(request):
    request.data.update({"owner": request.user})
    reserves_serializer = CreateReservesSerializer(data=request.data)
    if not reserves_serializer.is_valid():
        return Response(
            exception={"error": ErrorResponse.INVALID_DATA},
            status=status.HTTP_406_NOT_ACCEPTABLE,
        )
    create_response = reserves_serializer.create(
        reserves_serializer.validated_data, owner=request.user
    )
    if not create_response:
        return Response(
            exception={"error": ErrorResponse.INVALID_DATA},
            status=status.HTTP_406_NOT_ACCEPTABLE,
        )
    if create_response[0] == 0 and create_response[1] != 0:
        return Response(
            exception={"error": ErrorResponse.COLLISION_Messaage},
            status=status.HTTP_409_CONFLICT,
        )
    return Response(
        data={
            "created_reserve_count": create_response[0],
            "conflict_period_count": create_response[1],
        },
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
def get_all_reserves(request):
    # reserves_serializer = GetAllReservesSerializer(data=request.data)
    # if not reserves_serializer.is_valid():
    #     return Response(
    #         exception={"error": ErrorResponse.INVALID_DATA},
    #         status=status.HTTP_406_NOT_ACCEPTABLE,
    #     )
    fill, available, next = ReserveFeatureSeriallizer.get_a_day_data(
        date=timezone.datetime.now().date(), owner=request.user
    )
    past_reserves = Reservation.objects.filter(
        end_datetime__lte=timezone.datetime.now()
    ).order_by("-start_datetime")
    feature_reserves = Reservation.objects.filter(
        end_datetime__gt=timezone.datetime.now()
    ).order_by("start_datetime")
    paginator = PageNumberPagination()
    paginator.page_size = reserves_serializer.validated_data["page_count"]
    paginator.page = reserves_serializer.validated_data["page_count"]
    paginated_past = paginator.paginate_queryset(past_reserves)
    # paginated_feature = paginator.paginate_queryset(feature_reserves
