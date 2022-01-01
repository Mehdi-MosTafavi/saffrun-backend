from math import ceil

from core.responses import ErrorResponse
from core.serializers import GetAllSerializer
from core.services import is_user_employee
from drf_yasg.utils import swagger_auto_schema
from profile.models import EmployeeProfile, UserProfile
from rest_framework import generics, status
# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Invoice
from .serializers import PayInvoiceSerializer, ListInvoice, ManyPaymentSerializer
from .utils import get_payments_of_employee


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


@swagger_auto_schema(
    method="get",
    query_serializer=GetAllSerializer,
    responses={406: ErrorResponse.INVALID_DATA, 400: ErrorResponse.USER_EMPLOYEE},
)
@api_view(["GET"])
def get_all_payments(request):
    payment_serializer = GetAllSerializer(data=request.GET)
    if not payment_serializer.is_valid():
        return Response(
            {"Error": ErrorResponse.INVALID_DATA},
            status=status.HTTP_406_NOT_ACCEPTABLE,
        )
    if is_user_employee(request.user):
        payments, payments_count = get_payments_of_employee(payment_serializer, request)
        serializer_result = ManyPaymentSerializer(
            data={"pages": ceil(payments_count / payment_serializer.validated_data['page_count']), "payments": payments}
        )
        if not serializer_result.is_valid():
            return Response(
                {"Error": ErrorResponse.INVALID_DATA},
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )
        return Response(
            serializer_result.data,
            status=status.HTTP_200_OK,
        )
