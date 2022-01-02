from django.db.models import Sum, Q
from django.utils import timezone
from event.models import Event
from event.serializers import SpecificEventSerializer
from profile.models import EmployeeProfile
from profile.models import UserProfile
from reserve.models import Reservation
from reserve.serializers import ReserveSerializer
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination

from .models import Invoice
from .serializers import TurnOverSerializer


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
        return 'رویداد'
    return 'نوبت'


def get_mode_serializer(payment):
    if is_event_mode(payment):
        return SpecificEventSerializer(instance=get_object_or_404(Event, id=payment.filters['id'])).data
    else:
        return ReserveSerializer(instance=get_object_or_404(Reservation, id=payment.filters['id'])).data


def get_list_year_month():
    month = timezone.now().month
    year = timezone.now().year
    months = []
    for i in range(5):
        if (month - i) > 0:
            months.append((year, month - i))
        else:
            months.append((year - 1, 12 + (month - i)))
    return months


def get_payments_of_user(request):
    user = get_object_or_404(UserProfile, user=request.user)
    payments = Invoice.objects.filter(debtor=user).order_by('-created_at')

    list_year_date = get_list_year_month()
    chart_months = []
    get_chart_data(chart_months, list_year_date, payments)
    final_result = []
    payment_event = 0
    payment_reserve = 0
    for payment in payments:
        if is_event_mode(payment):
            payment_event += payment.amount
        else:
            payment_reserve += payment.amount
        final_result.append({
            'type': get_type_mode(payment),
            'amount': payment.amount,
            'date': payment.created_at,
            'mode': get_mode_serializer(payment)
        })
    chart_months.reverse()
    return TurnOverSerializer(
        data={
            'payments': final_result,
            'event_payment': payment_event,
            'reserve_payment': payment_reserve,
            'total_payment': (payment_event + payment_reserve),
            'chart_data': chart_months
        }
    )


def get_chart_data(chart_months, list_year_date, payments):
    for year, month in list_year_date:
        month_payment_total = payments.filter(created_at__year=year, created_at__month=month).aggregate(
            sum_payment=Sum('amount'))
        chart_months.append(month_payment_total['sum_payment'] if month_payment_total['sum_payment'] else 0)


def get_date_query(year: int, month: int):
    start_in_year_query = Q(created_at__year=year)
    in_year_query = start_in_year_query
    start_in_month_query = Q(created_at__month=month)
    in_month_query = start_in_month_query
    date_query = in_month_query & in_year_query
    return date_query


def get_payment_owner(employee, year, month):
    date_query = get_date_query(year, month)
    payment_sum = Invoice.objects.filter(owner=employee).filter(date_query).aggregate(payment_sum=Sum("amount"))[
        "payment_sum"]
    return payment_sum if payment_sum else 0


def get_yearly_payment_details(employee: EmployeeProfile, year: int) -> dict:
    result_list = []
    for month in range(12):
        payment_month = get_payment_owner(employee, year, month + 1)
        result_list.append(payment_month)
    now = timezone.now()
    current_month = get_payment_owner(employee, now.year, now.month)
    if now.month == 1:
        past_month = get_payment_owner(employee, now.year - 1, now.month - 1)
    else:
        past_month = get_payment_owner(employee, now.year, now.month - 1)

    return {
        'data': result_list,
        'current_month': current_month,
        'past_month': past_month
    }
