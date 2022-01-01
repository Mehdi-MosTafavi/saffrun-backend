from django.urls import path

from . import views

app_name = 'payment'

urlpatterns = [
    path('', views.Payment.as_view(mode=None), name="payment"),
    path('event/', views.Payment.as_view(mode="event"), name="payment_event"),
    path('reserve/', views.Payment.as_view(mode="reserve"), name="payment_reserve"),
    path('event/<int:mode_id>/', views.Payment.as_view(mode="event"), name="payment_get_reserve"),
    path('reserve/<int:mode_id>/', views.Payment.as_view(mode="reserve"), name="payment_get_reserve"),
]
