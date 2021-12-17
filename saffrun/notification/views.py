from django.shortcuts import render

# Create your views here.
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from core.responses import ErrorResponse
from core.services import is_user_client, is_user_employee
from .serializers import AddNotificationTokenSerializer, NotificationSerializer
from .utils import add_token_to_user, send_notif


class SetUserNotificationToken(APIView):
    @swagger_auto_schema(
        request_body=AddNotificationTokenSerializer,
        responses={
            200: "Done",
            406: ErrorResponse.INVALID_DATA,
            400: ErrorResponse.USER_CLIENT,
        },
    )
    def post(self, request):
        add_token_serializer = AddNotificationTokenSerializer(data=request.data)
        if not add_token_serializer.is_valid():
            return Response(
                {"status": "Error", "detail": ErrorResponse.INVALID_DATA},
                status=406,
            )
        if is_user_client(request.user):
            add_token_to_user(request.user.user_profile, add_token_serializer.validated_data.get("notification_token"))
            return Response({"status": "Done"}, status=200)
        else:
            return Response({"status": "Error", "detail":ErrorResponse.USER_CLIENT}, status=400)

class SendNotification(APIView):
    @swagger_auto_schema(
        request_body=NotificationSerializer,
        responses={
            200: "Done",
            406: ErrorResponse.INVALID_DATA,
            400: ErrorResponse.USER_EMPLOYEE,
            417: ErrorResponse.SERVER_ERROR
        },
    )
    def post(self, request):
        notification_serializer = NotificationSerializer(data=request.data)
        if not notification_serializer.is_valid():
            return Response(
                {"status": "Error", "detail": ErrorResponse.INVALID_DATA},
                status=406,
            )
        _type = notification_serializer.validated_data.get("type")
        text = notification_serializer.validated_data.get("text")
        title = notification_serializer.validated_data.get("title")
        url = notification_serializer.validated_data.get("url")
        if not (_type == 1 or _type == 2):
            return Response(
                {"status": "Error", "detail": ErrorResponse.INVALID_TYPE},
                status=400,
            )
        if is_user_employee(request.user):
            sent = send_notif(request.user.employee_profile, _type, title, text, url)
            if sent:
                return Response(
                    {"status": "Done"}, status=200,
                )
            return Response(
                {"status": "Error", "detail": ErrorResponse.SERVER_ERROR},
                status=417,
            )
        else:
            return Response(
                {"status": "Error", "detail": ErrorResponse.USER_EMPLOYEE},
                status=400,
            )
