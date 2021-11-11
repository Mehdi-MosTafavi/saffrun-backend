from .models import Event


def get_all_events_of_specific_day(user, date):
    return Event.objects.filter(participants=user).filter(
        start_datetime__date__lte=date, end_datetime__date__gte=date
    )
