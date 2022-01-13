from django.db.models import Q, Count, Sum, F

from event.models import Event

from reserve.models import Reservation
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from profile.models import RateEmployee, UserProfile, EmployeeProfile, Business

from category.models import Category

from event.serializers import EventImageSerializer
from profile.serializers import GetBusinessSerializer


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
        event_count = get_event_participant_count(employee, year, month + 1)
        reserve_count = get_reserve_participant_count(employee, year, month + 1)
        result_list.append({
            "event": event_count,
            "reserve": reserve_count
        })
    return result_list


def filter_event_datetime_query(from_datetime, until_datetime):
    if not from_datetime and not until_datetime:
        return Q()
    start_between_query = Q(start_datetime__gte=from_datetime) & Q(start_datetime__lte=until_datetime)
    start_before_query = Q(start_datetime__lt=from_datetime)
    end_after_query = Q(end_datetime__gt=from_datetime)
    return start_between_query | (start_before_query & end_after_query)

def filter_business_datetime_query(from_datetime, until_datetime):
    if not from_datetime and not until_datetime:
        return Q()
    reserve_capacity_query = Q(owner__owned_reserves__capacity__gt=F('participants_count'))
    reserve_from_datetime_query = Q(owner__owned_reserves__start_datetime__gte=from_datetime)
    reserve_until_datetime_query = Q(owner__owned_reserves__end_datetime__lte=until_datetime)
    reserve_datetime_query = reserve_from_datetime_query & reserve_until_datetime_query
    return reserve_capacity_query & reserve_datetime_query

def filter_category_query(category_id):
    if not category_id:
        return Q()
    category = get_object_or_404(Category.objects.all(), pk=category_id)
    return Q(category=category)


def get_events_for_search(search_query, category_id, sort, from_datetime, until_datetime):
    return Event.objects.filter(
        Q(title__icontains=search_query) &
        filter_category_query(category_id) &
        filter_event_datetime_query(from_datetime, until_datetime)
    ).order_by(sort.value)[:5]

def get_businesses_for_search(search_query, category_id, sort, from_datetime, until_datetime):
    return Business.objects.annotate(
        participants_count=Count('owner__owned_reserves__participants')
    ).filter(
        Q(title__icontains=search_query) &
        filter_category_query(category_id) &
        filter_business_datetime_query(from_datetime, until_datetime)
    ).order_by(sort.value if sort.value=='title' else 'id')[:5]

def get_event_businesses_list(search_query, category_id, sort, from_datetime, until_datetime):
    events = get_events_for_search(search_query, category_id, sort, from_datetime, until_datetime)
    businesses = get_businesses_for_search(search_query, category_id, sort, from_datetime, until_datetime)
    serialized_events = EventImageSerializer(events, many=True).data
    serialized_businesses = GetBusinessSerializer(businesses, many=True).data
    return {
        'events': serialized_events,
        'businesses': serialized_businesses
    }
