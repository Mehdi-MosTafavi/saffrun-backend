from django.db.models import Avg, Count

from .models import EmployeeProfile, UserProfile, RateEmployee
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

def remove_follower_user(user: UserProfile, employee: EmployeeProfile):
    employee.followers.remove(user)


def get_employee_rate_count(employee: EmployeeProfile) -> int:
    return RateEmployee.objects.filter(employee=employee).aggregate(count_rate=Count('rate'))['count_rate']

def calculate_employee_rate(employee: EmployeeProfile) -> int:
    rate_count = get_employee_rate_count(employee)

    return None if rate_count == 0 else \
        RateEmployee.objects.filter(employee=employee).aggregate(avg_rate=Avg('rate'))["avg_rate"]


def rate_employee(employee_id: int, user_profile: UserProfile, rate: float) -> Response:
    employee = get_object_or_404(EmployeeProfile, pk=employee_id)
    try:
        rate_object = RateEmployee.objects.get(employee=employee, client=user_profile)
        rate_object.rate = rate
    except:
        rate_object = RateEmployee.objects.create(employee=employee, client=user_profile, rate=rate)
    rate_object.save()

    return Response({
        "new_rate": calculate_employee_rate(employee)
    }, status=200)
