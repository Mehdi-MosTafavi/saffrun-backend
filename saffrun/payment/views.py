from rest_framework import generics
# Create your views here.
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import PayInvoiceSerializer, ListInvoice
from profile.models import EmployeeProfile, UserProfile
from .models import Invoice


class Payment(generics.ListCreateAPIView):
    permission_classes = (IsAuthenticated,)
    mode = None

    def __init__(self, mode):
        super().__init__()
        self.profile = None
        self.mode_id = None
        self.mode = mode

    def _get_profile(self):
        try:
            return EmployeeProfile.objects.get(user=self.request.user)
        except EmployeeProfile.DoesNotExist:
            try:
                return UserProfile.objects.get(user=self.request.user)
            except UserProfile.DoesNotExist:
                raise Exception('No profile Found!')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PayInvoiceSerializer
        if self.request.method == 'GET':
            return ListInvoice
        return super().get_serializer_class()

    def get_queryset(self):
        self.mode_id = self.kwargs.get('mode_id')
        self.profile = self._get_profile()
        if isinstance(self.profile, EmployeeProfile):
            query = Invoice.objects.filter(owner=self.profile.id)
        else:
            query = Invoice.objects.filter(debtor=self.profile.id)
        if self.mode:
            query = query.filter(filters__mode=self.mode)
        if self.mode_id:
            query = query.filter(filters__id=self.mode_id)
        return query

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer_class()
        response = serializer(queryset, many=True)
        return Response(response.data)