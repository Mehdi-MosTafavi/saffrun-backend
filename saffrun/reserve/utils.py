from datetime import timedelta

from django.db.models import Q, Count, F
from django.utils import timezone
from event.models import Event
from profile.models import EmployeeProfile
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


def get_a_day_data_for_future(date, owner):
    day_dic = get_a_day_data(date, owner)
    is_full_query = Q(participant_count=F("capacity"))
    reserve_list = (
        Reservation.objects.filter(
            owner=owner,
            start_datetime__gte=timezone.now(),
            start_datetime__date=date,
        )
            .annotate(participant_count=Count("participants"))
            .filter(~is_full_query)
            .order_by("start_datetime")
    )
    if reserve_list.count():
        time = reserve_list[0].get_start_datetime().time()
    else:
        time = None
    day_dic.update({"next_reserve": time})
    return day_dic


def get_details_past(dates, **kwargs):
    final_list = []
    for date in dates:
        final_list.append(get_a_day_data(date, kwargs["owner"]))
    return final_list


def get_details_future(dates, **kwargs):
    final_list = []
    for date in dates:
        final_list.append(get_a_day_data_for_future(date, kwargs["owner"]))
    return final_list


def get_past_result(owner):
    return (
        Reservation.objects.filter(
            end_datetime__lte=timezone.datetime.now(), owner=owner
        )
            .values("start_datetime__date")
            .distinct()
            .order_by("-start_datetime__date")
            .values_list("start_datetime__date", flat=True)
    )


def get_future_result(owner):
    return (
        Reservation.objects.filter(
            end_datetime__gt=timezone.datetime.now(), owner=owner
        )
            .values("start_datetime__date")
            .distinct()
            .order_by("start_datetime__date")
            .values_list("start_datetime__date", flat=True)
    )


def get_paginated_reservation_result(reserves_serializer, request):
    past_reserves = get_past_result(request.user.employee_profile)
    future_reserves = get_future_result(request.user.employee_profile)
    paginator = PageNumberPagination()
    paginator.page_size = reserves_serializer.validated_data["page_count"]
    paginator.page = reserves_serializer.validated_data["page"]
    paginated_past = paginator.paginate_queryset(past_reserves, request)
    paginated_future = paginator.paginate_queryset(future_reserves, request)
    past_result = get_details_past(
        paginated_past, owner=request.user.employee_profile
    )
    future_result = get_details_future(
        paginated_future, owner=request.user.employee_profile
    )
    return past_result, future_result


def get_user_busy_dates_list(user):
    reservation_dates = (
        Reservation.objects.filter(participants=user)
            .values_list("start_datetime__date", flat=True)
            .distinct()
    )
    event_dates_tuples = (
        Event.objects.filter(participants=user)
            .values_list("start_datetime__date", "end_datetime__date")
            .distinct()
    )
    event_dates = set()
    for event in event_dates_tuples:
        date = event[0]
        while date <= event[1]:
            event_dates.add(date)
            date += timedelta(days=1)
    dates_set = set()
    dates_set.update(reservation_dates)
    dates_set.update(event_dates)
    dates_set = list(dates_set)
    dates_set.sort()
    return dates_set


def get_all_user_reserves_in_a_day(user, date):
    return Reservation.objects.filter(
        participants=user, start_datetime__date=date
    ).order_by("start_datetime")


def get_reserve_count_and_duration(validated_data, total_duration):
    if validated_data["period_count"]:
        count = int(validated_data["period_count"])
        duration = total_duration // count
        return count, duration
    else:
        duration = validated_data["duration"]
        count = total_duration // duration
        return count, duration


def create_reserve_objects(
        validated_data, total_duration, start_datetime, **kwargs
):
    time = start_datetime
    count, duration = get_reserve_count_and_duration(
        validated_data, total_duration
    )
    for i in range(count):
        end_time = time + timedelta(minutes=duration)
        Reservation.objects.create(
            start_datetime=time,
            end_datetime=end_time,
            capacity=validated_data["capacity"],
            owner=kwargs["owner"],
        )
        time += timedelta(minutes=duration)
    return count


def get_nearest_free_reserve(admin_id):
    try:
        admin = EmployeeProfile.objects.get(user=admin_id)
        reserves = (
            Reservation.objects.filter(
                owner=admin, start_datetime__gte=timezone.datetime.now()
            )
                .annotate(participant_count=Count("participants"))
                .filter(participant_count__lt=F("capacity"))
                .order_by("start_datetime")
        )
        if reserves.count() == 0:
            return None
        return reserves[0]
    except:
        return False


def get_next_n_days_free_reserves(admin_id, days):
    admin = EmployeeProfile.objects.get(user=admin_id)
    today_date = timezone.datetime.now().date()
    reserves = (
        Reservation.objects.filter(
            owner=admin,
            start_datetime__gte=timezone.datetime.now(),
            start_datetime__date__lt=today_date + timedelta(days=days),
        )
            .annotate(participant_count=Count("participants"))
            .filter(participant_count__lt=F("capacity"))
            .order_by("start_datetime")
    )
    reserves_list = [[] for i in range(days)]
    for reserve in reserves.all():
        index = (reserve.start_datetime.date() - today_date).days
        reserves_list[index].append(reserve)
    return reserves_list


def reserve_it(user, reserve_id):
    try:
        reservation = Reservation.objects.get(id=reserve_id)
        if reservation.capacity > reservation.participants.count():
            reservation.participants.add(user)
            reservation.save()
            return True
        else:
            return False
    except:
        return False


def get_reserve_abstract_dictionary(reserve):
    return (
        {"reserve_id": reserve.id, "datetime": reserve.get_start_datetime()}
        if reserve
        else ""
    )


def get_current_reserve(owner_profile: EmployeeProfile):
    current_time = timezone.datetime.now()
    reserve = Reservation.objects.filter(start_datetime__lte=current_time, end_datetime__gte=current_time,
                                         owner=owner_profile).annotate(participant_count=Count("participants"))
    if len(reserve) == 0:
        return None
    return reserve[0]


def get_nearest_busy_reserve(owner_profile: EmployeeProfile):
    current_time = timezone.datetime.now()
    reserve_list = Reservation.objects.filter(start_datetime__gte=current_time, start_datetime__date=current_time.date(),
                                         owner=owner_profile).annotate(participant_count=Count("participants")).filter(
        participant_count__gte = 0
    )
    return reserve_list if len(reserve_list) <= 5 else reserve_list[:5]
