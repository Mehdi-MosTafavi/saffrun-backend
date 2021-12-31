from rest_framework import generics
# Create your views here.
from rest_framework.permissions import IsAuthenticated
from .serializers import PayInvoiceSerializer


class Payment(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PayInvoiceSerializer