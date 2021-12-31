from django.urls import path
from . import views

app_name = 'payment'

urlpatterns = [
    path('invoice/', views.Payment.as_view(), name='add_payment')
]
