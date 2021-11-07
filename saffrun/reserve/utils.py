from django.db.models import Q

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
