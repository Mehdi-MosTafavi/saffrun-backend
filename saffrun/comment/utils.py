from datetime import timezone

from django.db.models import Q, Count, F
from rest_framework.pagination import PageNumberPagination

from .models import Comment
from ..event.models import Event
from ..profile.models import EmployeeProfile


def save_a_comment(validated_data: map, user):
    if "event_id" in validated_data:
        event = Event.objects.get(id=validated_data["event_id"])
        Comment.objects.create(
            content=validated_data["content"],
            is_parent=True,
            event=event,
            user=user
        )
    elif "owner_id" in validated_data:
        profile = EmployeeProfile.objects.get(id=validated_data["owner_id"])
        Comment.objects.create(
            content=validated_data["content"],
            is_parent=True,
            owner=profile,
            user=user
        )
    else:
        raise Exception("incorrect args")

def save_a_reply(validated_data: map, owner, comment):
    reply = Comment.objects.create(
        content=validated_data["content"],
        is_parent=False,
        owner=comment.owner,
        event=comment.event
    )
    comment.reply = reply
    comment.save()

def get_a_day_data_event_comment(date, event):
    all = Comment.objects.filter(
        event=event, start_datetime__date=date
    ).count()
    fill = (
        Comment.objects.filter(event=event, start_datetime__date=date)
        .annotate(participant_count=Count("participants"))
        .filter(participant_count=F("capacity"))
        .count()
    )
    available = all - fill
    return {"date": date, "fill": fill, "available": available}

def get_a_day_data_for_future_event_comment(date, event):
    day_dic = get_a_day_data_event_comment(date, event)
    is_full_query = Q(participant_count=F("capacity"))
    reserve_list = (
        Comment.objects.filter(
            event=event,
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

def get_event_comment_details_past(dates, **kwargs):
    final_list = []
    for date in dates:
        final_list.append(get_a_day_data_event_comment(date, kwargs["event"]))
    return final_list

def get_event_comment_details_future(dates, **kwargs):
    final_list = []
    for date in dates:
        final_list.append(get_a_day_data_for_future_event_comment(date, kwargs["event"]))
    return final_list

def get_future_event_comments(event):
    return (
        Comment.objects.filter(
            event__id=event.id, is_parent=True
        )
            .values("start_datetime__date")
            .distinct()
            .order_by('-updated_at')
            .values_list("start_datetime__date", flat=True)
    )

def get_past_event_comments(event):
    return (
        Comment.objects.filter(
            event__id=event.id, is_parent=True
        )
            .values("start_datetime__date")
            .distinct()
            .order_by('-updated_at')
            .values_list("start_datetime__date", flat=True)
    )

def get_paginated_event_comments(event):
    past_comments = get_past_event_comments(event)
    future_comments = get_future_event_comments(event)
    paginator = PageNumberPagination()
    paginator.page_size = event.validated_data["page_count"]
    paginator.page = event.validated_data["page_count"]
    paginated_past = paginator.paginate_queryset(past_comments, event)
    paginated_future = paginator.paginate_queryset(future_comments, event)
    past_result = get_event_comment_details_past(
        paginated_past, event
    )
    future_result = get_event_comment_details_future(
        paginated_future, event
    )
    return past_result, future_result

def get_event_comments(event):
    return Comment.objects.filter(event__id=event.id, is_parent=True).order_by('-updated_at')

def get_a_day_data_owner_comment(date, owner):
    all = Comment.objects.filter(
        owner=owner, start_datetime__date=date
    ).count()
    fill = (
        Comment.objects.filter(owner=owner, start_datetime__date=date)
        .annotate(participant_count=Count("participants"))
        .filter(participant_count=F("capacity"))
        .count()
    )
    available = all - fill
    return {"date": date, "fill": fill, "available": available}

def get_a_day_data_for_future_owner_comment(date, owner):
    day_dic = get_a_day_data_event_comment(date, owner)
    is_full_query = Q(participant_count=F("capacity"))
    reserve_list = (
        Comment.objects.filter(
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

def get_owner_comment_details_past(dates, **kwargs):
    final_list = []
    for date in dates:
        final_list.append(get_a_day_data_event_comment(date, kwargs["owner"]))
    return final_list

def get_owner_comment_details_future(dates, **kwargs):
    final_list = []
    for date in dates:
        final_list.append(get_a_day_data_for_future_event_comment(date, kwargs["owner"]))
    return final_list

def get_future_owner_comments(owner):
    return (
        Comment.objects.filter(
            owner__id=owner.id, is_parent=True
        )
            .values("start_datetime__date")
            .distinct()
            .order_by('-updated_at')
            .values_list("start_datetime__date", flat=True)
    )

def get_past_owner_comments(owner):
    return (
        Comment.objects.filter(
            owner__id=owner.id, is_parent=True
        )
            .values("start_datetime__date")
            .distinct()
            .order_by('-updated_at')
            .values_list("start_datetime__date", flat=True)
    )

def get_paginated_owner_comments(owner):
    past_comments = get_past_owner_comments(owner)
    future_comments = get_future_owner_comments(owner)
    paginator = PageNumberPagination()
    paginator.page_size = owner.validated_data["page_count"]
    paginator.page = owner.validated_data["page_count"]
    paginated_past = paginator.paginate_queryset(past_comments, owner)
    paginated_future = paginator.paginate_queryset(future_comments, owner)
    past_result = get_owner_comment_details_past(
        paginated_past, owner
    )
    future_result = get_owner_comment_details_future(
        paginated_future, owner
    )
    return past_result, future_result

def get_owner_comments(owner):
    return Comment.objects.filter(owner__id=owner.id, is_parent=True).order_by('-updated_at')

