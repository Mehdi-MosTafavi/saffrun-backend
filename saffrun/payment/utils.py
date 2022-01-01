import random
import string

from profile.models import EmployeeProfile
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination

from .models import Invoice


def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def get_payments_of_employee(serializer, request):
    employee = get_object_or_404(EmployeeProfile, user=request.user)
    payments = Invoice.objects.filter(owner=employee).order_by('-created_at')
    list_dates = payments.values_list("created_at__date", flat=True).distinct()
    paginator = PageNumberPagination()
    paginator.page_size = serializer.validated_data.get("page_count")
    paginator.page = serializer.validated_data.get("page")
    paginated_payments = paginator.paginate_queryset(list_dates, request)
    final_result = []
    for date in paginated_payments:
        payment_of_date = payments.filter(created_at__date=date)
        payment_detail = []
        count_event = 0
        count_reserve = 0
        total_payment = 0
        count_event, count_reserve, total_payment = detail_payment_of_date(count_event, count_reserve, payment_detail,
                                                                           payment_of_date, total_payment)
        final_result.append({
            'date': date,
            'count_event': count_event,
            'count_reserve': count_reserve,
            'total_payment': total_payment,
            'payment_detail': payment_detail
        })
    return final_result, list_dates.count()


def detail_payment_of_date(count_event, count_reserve, payment_detail, payment_of_date, total_payment):
    for payment in payment_of_date:
        if is_event_mode(payment):
            count_event += 1
        else:
            count_reserve += 1
        total_payment += payment.amount
        payment_detail.append(
            {
                'name': payment.debtor.user.get_full_name(),
                'type': get_type_mode(payment),
                'time': payment.created_at,
                'amount': payment.amount
            }
        )
    return count_event, count_reserve, total_payment


def is_event_mode(payment):
    return payment.filters['mode'] == 'event'


def get_type_mode(payment):
    if is_event_mode(payment):
        return 'نوبت'
    return 'رویداد'
