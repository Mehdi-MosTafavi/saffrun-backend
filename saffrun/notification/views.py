from django.shortcuts import render

# Create your views here.
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from core.responses import ErrorResponse
from core.services import is_user_client
from notification.serializers import AddNotificationTokenSerializer
from notification.utils import add_token_to_user


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
