from django.urls import path

from . import views
from .views import get_all_payments, get_all_payments_user

app_name = 'payment'

urlpatterns = [
    path('', views.Payment.as_view(mode=None), name="payment"),
    path('event/', views.Payment.as_view(mode="event"), name="payment_event"),
    path('reserve/', views.Payment.as_view(mode="reserve"), name="payment_reserve"),
    path('event/<int:mode_id>/', views.Payment.as_view(mode="event"), name="payment_get_reserve"),
    path('reserve/<int:mode_id>/', views.Payment.as_view(mode="reserve"), name="payment_get_reserve"),
    path('web/get-all-payment/', get_all_payments, name='all-payment'),
    path('client/get-all-payment/', get_all_payments_user, name='all-payment-user'),
    path("web/get-yearly-details/", views.GetYearlyDetails.as_view(), name="get-yearly-details"),

]
