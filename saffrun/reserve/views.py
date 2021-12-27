from core.responses import ErrorResponse, SuccessResponse
from drf_yasg.utils import swagger_auto_schema
from event.services import get_all_events_of_specific_day
from profile.models import EmployeeProfile
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    CreateReservesSerializer,
    DateSerializer,
    DayDetailSerializer,
    DaySerializer,
    GetAdminSerializer,
    NextSevenDaysSerializer,
    ReserveEmployeeSerializer, ReserveOwnerDetail, CurrentNearestReserveSerializer, AbstractReserveSerializer,
    ReserveFutureSeriallizer, ReserveHistorySerializer,
)
from core.serializers import GetAllSerializer
from .utils import (
    get_user_busy_dates_list,
    get_all_user_reserves_in_a_day,
    get_nearest_free_reserve,
    get_next_n_days_free_reserves,
    reserve_it,
    get_reserve_abstract_dictionary, get_current_reserve, get_nearest_busy_reserve,
    get_paginated_past_reservation_result, get_paginated_future_reservation_result, get_reserve_history_client,
)
from core.services import is_user_client


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
        reserves_serializer.validated_data, owner=request.user.employee_profile
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
    query_serializer=GetAllSerializer,
    responses={
        status.HTTP_200_OK: AbstractReserveSerializer,
        status.HTTP_406_NOT_ACCEPTABLE: ErrorResponse.INVALID_DATA,
    },
)
@api_view(["GET"])
def get_past_reserves(request):
    reserves_serializer = GetAllSerializer(data=request.GET)
    if not reserves_serializer.is_valid():
        return Response(
            exception={"error": ErrorResponse.INVALID_DATA},
            status=status.HTTP_406_NOT_ACCEPTABLE,
        )
    past_result = get_paginated_past_reservation_result(
        reserves_serializer, request
    )
    return Response({"reserves": past_result}, status=200)

@swagger_auto_schema(
    method="get",
    query_serializer=GetAllSerializer,
    responses={
        status.HTTP_200_OK: ReserveFutureSeriallizer,
        status.HTTP_406_NOT_ACCEPTABLE: ErrorResponse.INVALID_DATA,
    },
)
@api_view(["GET"])
def get_future_reserves(request):
    reserves_serializer = GetAllSerializer(data=request.GET)
    if not reserves_serializer.is_valid():
        return Response(
            exception={"error": ErrorResponse.INVALID_DATA},
            status=status.HTTP_406_NOT_ACCEPTABLE,
        )
    future_result = get_paginated_future_reservation_result(
        reserves_serializer, request
    )
    return Response({"reserves": future_result}, status=200)

@swagger_auto_schema(
    method="get",
    responses={
        status.HTTP_200_OK: DateSerializer,
        status.HTTP_406_NOT_ACCEPTABLE: ErrorResponse.INVALID_DATA,
    },
)
@api_view(["GET"])
def get_user_busy_dates(request):
    user_busy_dates = get_user_busy_dates_list(request.user.user_profile)
    dates_serializer = DateSerializer(data={"dates": user_busy_dates})
    if not dates_serializer.is_valid():
        return Response(
            exception={"error": ErrorResponse.INVALID_DATA},
            status=status.HTTP_406_NOT_ACCEPTABLE,
        )
    return Response(data=dates_serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method="get",
    query_serializer=DaySerializer,
    responses={
        status.HTTP_200_OK: DayDetailSerializer,
        status.HTTP_406_NOT_ACCEPTABLE: ErrorResponse.INVALID_DATA,
    },
)
@api_view(["GET"])
def get_detail_of_a_day(request):
    day_serializer = DaySerializer(data=request.GET)
    if not day_serializer.is_valid():
        return Response(
            exception={
                "error": ErrorResponse.INVALID_DATA,
            },
            status=status.HTTP_406_NOT_ACCEPTABLE,
        )
    date = day_serializer.validated_data["date"]
    events = get_all_events_of_specific_day(request.user.user_profile, date)
    reserves = get_all_user_reserves_in_a_day(request.user.user_profile, date)
    day_detail_serializer = DayDetailSerializer(
        instance={
            "events": events,
            "reserves": reserves,
        }
    )
    return Response(data=day_detail_serializer.data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method="get",
    query_serializer=GetAdminSerializer,
    responses={
        status.HTTP_200_OK: NextSevenDaysSerializer,
        status.HTTP_406_NOT_ACCEPTABLE: ErrorResponse.INVALID_DATA,
    },
)
@api_view(["GET"])
def get_next_seven_days(request):
    admin_serializer = GetAdminSerializer(data=request.GET)
    if not admin_serializer.is_valid():
        return Response(
            exception={
                "error": ErrorResponse.INVALID_DATA,
            },
            status=status.HTTP_406_NOT_ACCEPTABLE,
        )
    admin_id = admin_serializer.validated_data.get("admin_id")
    next_reserve = get_nearest_free_reserve(admin_id)
    next_seven_days_list = get_next_n_days_free_reserves(admin_id, 7)
    nearest_dictionary = get_reserve_abstract_dictionary(next_reserve)
    next_seven_days_dictionary_list = []
    for i in range(7):
        next_seven_days_dictionary_list.append(
            list(map(get_reserve_abstract_dictionary, next_seven_days_list[i]))
        )
    final_data = {
        "nearest": nearest_dictionary,
        "next_seven_days": next_seven_days_dictionary_list,
    }
    return Response(final_data, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method="post",
    request_body=ReserveEmployeeSerializer,
    responses={
        status.HTTP_201_CREATED: SuccessResponse.RESERVED,
        status.HTTP_406_NOT_ACCEPTABLE: ErrorResponse.INVALID_DATA,
        status.HTTP_411_LENGTH_REQUIRED: ErrorResponse.FULL_CAPACITY,
    },
)
@api_view(["POST"])
def reserve_employee(request):
    reserve_employee_serializer = ReserveEmployeeSerializer(data=request.data)
    if not reserve_employee_serializer.is_valid():
        return Response(
            exception={
                "error": ErrorResponse.INVALID_DATA,
            },
            status=status.HTTP_406_NOT_ACCEPTABLE,
        )
    is_reserved = reserve_it(
        request.user.user_profile,
        reserve_employee_serializer.validated_data.get("reserve_id"),
    )
    if is_reserved:
        return Response(
            {"success": SuccessResponse.RESERVED}, status=status.HTTP_200_OK
        )
    return Response(
        {"error": ErrorResponse.FULL_CAPACITY},
        status=status.HTTP_411_LENGTH_REQUIRED,
    )


@swagger_auto_schema(
    method="get",
    responses={
        status.HTTP_200_OK: ReserveOwnerDetail,
        status.HTTP_406_NOT_ACCEPTABLE: ErrorResponse.INVALID_DATA,
    },
)
@api_view(["GET"])
def get_nearest_reserve(request):
    owner = get_object_or_404(EmployeeProfile, user=request.user)
    current_reserve = get_current_reserve(owner)
    near_reserve = get_nearest_busy_reserve(owner)
    day_detail_serializer = CurrentNearestReserveSerializer(
        instance={
            "current_reserve": current_reserve,
            "nearest_reserves": near_reserve
        }
    )
    return Response(day_detail_serializer.data, status=status.HTTP_200_OK)


class ClientReserveHistory(APIView):
    @swagger_auto_schema(
        query_serializer=GetAllSerializer,
        responses={
            status.HTTP_200_OK: ReserveHistorySerializer,
            status.HTTP_400_BAD_REQUEST: ErrorResponse.USER_CLIENT,
            status.HTTP_406_NOT_ACCEPTABLE: ErrorResponse.INVALID_DATA,
        }
    )
    def get(self, request):
        reserves_serializer = GetAllSerializer(data=request.GET)
        if not reserves_serializer.is_valid():
            return Response(
                exception={"error": ErrorResponse.INVALID_DATA},
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )
        if not is_user_client(request.user):
            return Response(
                {"status": "Error", "detail": ErrorResponse.USER_CLIENT},
                status=status.HTTP_400_BAD_REQUEST,
            )
        reserves = get_reserve_history_client(request.user.user_profile)
        paginator = PageNumberPagination()
        paginator.page_size = reserves_serializer.validated_data["page_count"]
        paginator.page = reserves_serializer.validated_data["page"]
        reserves = paginator.paginate_queryset(reserves, request)
        return Response({"events": ReserveHistorySerializer(reserves, many=True).data}, status=200)
