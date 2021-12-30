from django.urls import path

from . import views
from .views import remove_all_reserve_of_date, remove_reserve

app_name = "reserve"
urlpatterns = [
    path("create/", views.create_reserves, name="create-reserves"),
    path("get-past-reserves/", views.get_past_reserves, name="get-past-reserves"),
    path("get-future-reserves/", views.get_future_reserves, name="get-future-reserves"),
    path("get-busy-dates/", views.get_user_busy_dates, name="user-busy-dates"),
    path("get-day-detail/", views.get_detail_of_a_day, name="get-day-detail"),
    path(
        "get-next-seven-days/", views.get_next_seven_days, name="get-next-days"
    ),
    path("reserve-employee/", views.reserve_employee, name="reserve-employee"),
    path("get-nearest-reserve/", views.get_nearest_reserve, name="get-near-reserve"),
    path('get-client-reserve-history', views.ClientReserveHistory.as_view(), name='client-reserve-history'),
    path('web/get-reserve-detail', views.ReserveDetail.as_view(), name='reserve-detail'),
    path('web/remove-all-reserve-date', remove_all_reserve_of_date, name='remove-date-reserve'),
    path('web/remove-reserve', remove_reserve, name='remove-reserve'),
    path('web/get-reserve-table-detail', views.ResarvationTableReserveDetail.as_view(), name='get-table-detail')
]
