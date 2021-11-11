from django.db.models import Q, Count, F
from django.utils import timezone
from django.utils.datetime_safe import datetime
from rest_framework.pagination import PageNumberPagination

from .models import Reservation


def check_collision(wanted_start, wanted_end, owner):
    is_owner = Q(owner=owner)
    right_collision = Q(start_datetime__gt=wanted_start) & Q(
        start_datetime__lt=wanted_end
    )
    left_collision = Q(end_datetime__gt=wanted_start) & Q(
        end_datetime__lt=wanted_end
    )
    full_collision = Q(start_datetime__lte=wanted_start) & Q(
        end_datetime__gte=wanted_end
    )
    reserves = Reservation.objects.filter(
        is_owner & (right_collision | left_collision | full_collision)
    )
    if reserves.count():
        return True
    return False


def get_a_day_data(date, owner):
    all = Reservation.objects.filter(
        owner=owner, start_datetime__date=date
    ).count()
    fill = (
        Reservation.objects.filter(owner=owner, start_datetime__date=date)
        .annotate(participant_count=Count("participants"))
        .filter(participant_count=F("capacity"))
        .count()
    )
    available = all - fill
    return {"date": date, "fill": fill, "available": available}


def get_a_day_data_for_feature(date, owner):
    day_dic = get_a_day_data(date, owner)
    is_full_query = Q(participant_count=F("capacity"))
    reserve_list = (
        Reservation.objects.filter(
            owner=owner, start_datetime__gte=timezone.now()
        )
        .annotate(participant_count=Count("participants"))
        .filter(~is_full_query)
        .order_by("start_datetime")
    )
    if len(reserve_list):
        time = reserve_list[0].get_start_datetime().time()
    else:
        time = ""
    day_dic.update({"next": time})
    return day_dic


def get_details_past(dates, **kwargs):
    final_list = []
    for date in dates:
        final_list.append(get_a_day_data(date, kwargs["owner"]))
    return final_list


def get_details_future(dates, **kwargs):
    final_list = []
    for date in dates:
        final_list.append(get_a_day_data_for_feature(date, kwargs["owner"]))
    return final_list


def get_past_result():
    return (
        Reservation.objects.filter(end_datetime__lte=timezone.datetime.now())
        .values("start_datetime__date")
        .distinct()
        .order_by("-start_datetime__date")
        .values_list("start_datetime__date", flat=True)
    )


def get_future_result():
    return (
        Reservation.objects.filter(end_datetime__gt=timezone.datetime.now())
        .values("start_datetime__date")
        .distinct()
        .order_by("start_datetime__date")
        .values_list("start_datetime__date", flat=True)
    )


def get_paginated_reservation_result(reserves_serializer, request):
    past_reserves = get_past_result()
    future_reserves = get_future_result()
    paginator = PageNumberPagination()
    paginator.page_size = reserves_serializer.validated_data["page_count"]
    paginator.page = reserves_serializer.validated_data["page_count"]
    paginated_past = paginator.paginate_queryset(past_reserves, request)
    paginated_future = paginator.paginate_queryset(future_reserves, request)
    past_result = get_details_past(paginated_past, owner=request.user)
    future_result = get_details_future(paginated_future, owner=request.user)
    return past_result, future_result
