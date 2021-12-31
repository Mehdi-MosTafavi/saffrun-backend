from django.db.models import Q, Count, Sum
from django.utils import timezone

from event.models import Event
from profile.models import EmployeeProfile

from reserve.models import Reservation

def get_date_query(year: int, month: int):
    start_in_year_query = Q(start_datetime__year=year)
    end_in_year_query = Q(end_datetime__year=year)
    between_year_query = Q(start_datetime__year__lt=year) & Q(end_datetime__year__gt=year)
    in_year_query = start_in_year_query | end_in_year_query | between_year_query
    start_in_month_query = Q(start_datetime__month=month)
    end_in_month_query = Q(end_datetime__month=month)
    between_month_query = Q(start_datetime__month__lt=month) & Q(end_datetime__month__gt=month)
    in_month_query = start_in_month_query | end_in_month_query | between_month_query
    date_query = in_month_query & in_year_query
    return date_query

def get_event_participant_count(employee: EmployeeProfile, year: int, month: int) -> int:
    date_query = get_date_query(year, month)
    event_count = Event.objects.filter(owner=employee).filter(date_query).annotate(
        participant_count=Count("participants")).aggregate(participant_sum=Sum("participant_count"))["participant_sum"]
    return event_count if event_count else 0

def get_reserve_participant_count(employee:EmployeeProfile, year:int, month:int) -> int:
    date_query = get_date_query(year, month)
    reservation_count = Reservation.objects.filter(owner=employee).filter(date_query).annotate(
        participant_count=Count("participants")).aggregate(participant_sum=Sum("participant_count"))["participant_sum"]
    return reservation_count if reservation_count else 0


def get_yearly_details(employee: EmployeeProfile, year:int) -> list:
    result_list = []
    for month in range(12):
        event_count = get_event_participant_count(employee, year, month)
        reserve_count = get_reserve_participant_count(employee, year, month)
        result_list.append({
            "event": event_count,
            "reserve":reserve_count
        })
    return result_list

