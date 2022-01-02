# Create your views here.
from math import ceil

from core.responses import ErrorResponse
from core.serializers import GetAllSerializer
from core.services import is_user_client, is_user_employee
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import AddNotificationTokenSerializer, SendNotificationSerializer, \
    EmployeeGetNotificationsSerializer, ClientGetNotificationSerializer
from .utils import add_token_to_user, send_notif, get_all_sent_notification, get_all_received_notification


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
            return Response({"status": "Error", "detail": ErrorResponse.USER_CLIENT}, status=400)


class SendNotification(APIView):
    @swagger_auto_schema(
        request_body=SendNotificationSerializer,
        responses={
            200: "Done",
            406: ErrorResponse.INVALID_DATA,
            400: ErrorResponse.USER_EMPLOYEE,
            417: ErrorResponse.SERVER_ERROR
        },
    )
    def post(self, request):
        notification_serializer = SendNotificationSerializer(data=request.data)
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


class EmployeeGetNotifications(APIView):
    @swagger_auto_schema(
        query_serializer=GetAllSerializer,
        responses={
            status.HTTP_200_OK: EmployeeGetNotificationsSerializer,
            status.HTTP_400_BAD_REQUEST: ErrorResponse.USER_EMPLOYEE,
            status.HTTP_406_NOT_ACCEPTABLE: ErrorResponse.INVALID_DATA,
        }
    )
    def get(self, request):
        serializer = GetAllSerializer(data=request.GET)
        if not serializer.is_valid():
            return Response(
                {"status": "Error", "detail": ErrorResponse.INVALID_DATA},
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )
        page = serializer.validated_data.get("page")
        page_count = serializer.validated_data.get("page_count")
        if is_user_employee(request.user):
            notifications, count_notifs = get_all_sent_notification(request.user.employee_profile, page, page_count,
                                                                    request)
            notification_serializer = EmployeeGetNotificationsSerializer(notifications, many=True)
            return Response({"pages": ceil(count_notifs / page_count), "notifications": notification_serializer.data},
                            status=status.HTTP_200_OK)
        else:
            return Response(
                {"status": "Error", "detail": ErrorResponse.USER_EMPLOYEE},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ClientGetNotifications(APIView):
    @swagger_auto_schema(
        query_serializer=GetAllSerializer,
        responses={
            status.HTTP_200_OK: ClientGetNotificationSerializer,
            status.HTTP_400_BAD_REQUEST: ErrorResponse.USER_CLIENT,
            status.HTTP_406_NOT_ACCEPTABLE: ErrorResponse.INVALID_DATA,
        }
    )
    def get(self, request):
        serializer = GetAllSerializer(data=request.GET)
        if not serializer.is_valid():
            return Response(
                {"status": "Error", "detail": ErrorResponse.INVALID_DATA},
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )
        page = serializer.validated_data.get("page")
        page_count = serializer.validated_data.get("page_count")
        if is_user_client(request.user):
            notifications = get_all_received_notification(request.user.user_profile, page, page_count, request)
            notification_serializer = ClientGetNotificationSerializer(notifications, many=True)
            return Response({"notifications": notification_serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"status": "Error", "detail": ErrorResponse.USER_CLIENT},
                status=status.HTTP_400_BAD_REQUEST,
            )
