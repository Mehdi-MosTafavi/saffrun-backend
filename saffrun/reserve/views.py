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
from .utils import (
    get_details_past,
    get_details_future,
    get_paginated_reservation_result,
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
    reserves_serializer = CreateReservesSerializer(data=request.data)
    if not reserves_serializer.is_valid():
        return Response(
            exception={
                "error": ErrorResponse.INVALID_DATA,
                "validation_errors": reserves_serializer.errors,
            },
            status=status.HTTP_406_NOT_ACCEPTABLE,
        )
    create_response = reserves_serializer.create(
        reserves_serializer.validated_data, owner=request.user
    )
    if not create_response:
        return Response(
            exception={
                "error": ErrorResponse.INVALID_DATA,
                "validation_errors": reserves_serializer.errors,
            },
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


@swagger_auto_schema(
    method="get",
    query_serializer=GetAllReservesSerializer,
    responses={
        status.HTTP_201_CREATED: SuccessResponse.CREATED,
        status.HTTP_406_NOT_ACCEPTABLE: ErrorResponse.INVALID_DATA,
    },
)
@api_view(["GET"])
def get_all_reserves(request):
    reserves_serializer = GetAllReservesSerializer(data=request.GET)
    if not reserves_serializer.is_valid():
        return Response(
            exception={"error": ErrorResponse.INVALID_DATA},
            status=status.HTTP_406_NOT_ACCEPTABLE,
        )
    past_result, future_result = get_paginated_reservation_result(
        reserves_serializer, request
    )
    return Response(
        {"past": past_result, "future": future_result},
        status=status.HTTP_200_OK,
    )
