from django.db import transaction
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics, status
from authentication.serializers import (
    RegisterSerializer,
)
from rest_framework.response import Response
from core.responses import ErrorResponse, SuccessResponse
from profile.models import EmployeeProfile, UserProfile

from .serializers import RecoverPasswordSerializer, ChangePasswordSerializer
from .tasks import send_email
from core.models import Business

from .utils import change_password


class RegisterUser(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def __init__(
            self,
    ):
        super().__init__()
        self.client_type = None

    def post(self, request, *args, **kwargs):
        self.client_type = request.data.get("client", None)
        if self.client_type is None:
            return Response(
                {"status": "Error", "detail": ErrorResponse.NO_CLIENT_HEADER},
                status=400,
            )
        return super().post(request, *args, **kwargs)

    def finalize_response(self, request, response, *args, **kwargs):
        if response.status_code == 201:
            response.data = {"status": "Done"}
        return super().finalize_response(request, response, *args, **kwargs)

    def perform_create(self, serializer):
        if not serializer.is_valid():
            raise
        user = serializer.create_instance()
        profile = None
        business = None
        if self.client_type == "web":
            profile = EmployeeProfile(user=user)
            business = Business(owner=profile)
        elif self.client_type == "app":
            profile = UserProfile(user=user)

        with transaction.atomic():
            user.save()
            profile.save()
            if business:
                business.save()
                profile.save()
        return


class ForgotPassword(generics.GenericAPIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        request_body=RecoverPasswordSerializer,
        responses={
            status.HTTP_400_BAD_REQUEST: ErrorResponse.USER_EMPLOYEE,
            status.HTTP_406_NOT_ACCEPTABLE: ErrorResponse.INVALID_DATA,
        }
    )
    def post(self, request):
        recover_serializer = RecoverPasswordSerializer(data=request.data)
        if not recover_serializer.is_valid():
            print(recover_serializer.errors)
            return Response({"status": "Error"})
        try:
            send_email.apply_async(args=[recover_serializer.validated_data['username']])
        except:
            return Response()
        return Response()

class ChangePassword(generics.GenericAPIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        request_body=ChangePasswordSerializer,
        responses={
            status.HTTP_200_OK: SuccessResponse.CHANGED,
            status.HTTP_406_NOT_ACCEPTABLE: ErrorResponse.INVALID_DATA,
        }
    )
    def post(self, request):
        change_password_serializer = ChangePasswordSerializer(data=request.data)
        if not change_password_serializer.is_valid():
            return Response(
                exception={"error": ErrorResponse.INVALID_DATA},
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )
        username = change_password_serializer.validated_data.get("username")
        old_password = change_password_serializer.validated_data.get("old_password")
        new_password = change_password_serializer.validated_data.get("new_password")
        return change_password(username, old_password, new_password)
