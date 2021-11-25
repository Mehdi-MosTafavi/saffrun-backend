from django.db import transaction
from rest_framework.generics import get_object_or_404, GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from core.responses import ErrorResponse
from profile.models import EmployeeProfile, UserProfile
from rest_framework.views import APIView
from .serializers import FollowSerializer


# Create your views here.


class UserView(APIView):
    permission_classes = (AllowAny, IsAuthenticated)

    def get_profile(self, headers):
        mode = headers["Client"]
        if mode == "web":
            profile = EmployeeProfile.objects.get(user=self.request.user)
        elif mode == "app":
            profile = UserProfile.objects.get(user=self.request.user)
        return profile

    def get(self, request):
        try:
            profile = self.get_profile(self.request.headers)
        except KeyError as err:
            return Response(
                {
                    "status": "Error",
                    "detail": ErrorResponse.NO_CLIENT_HEADER
                }, status=400)
        return Response(
            {
                "username": self.request.user.username,
                "first_name": self.request.user.first_name,
                "last_name": self.request.user.last_name,
                "email": self.request.user.email,
                "phone": profile.phone,
                "country": profile.country,
                "province": profile.province,
                "address": profile.address,
            }
        )

    def put(self, request):
        user = self.request.user
        try:
            profile = self.get_profile(self.request.headers)
        except KeyError as err:
            return Response(
                {
                    "status": "Error",
                    "detail": ErrorResponse.NO_CLIENT_HEADER
                }, status=400)
        try:
            user.username = self.request.data["username"]
            user.first_name = self.request.data["first_name"]
            user.last_name = self.request.data["last_name"]
            user.email = self.request.data["email"]
            profile.phone = self.request.data["phone"]
            profile.country = self.request.data["country"]
            profile.province = self.request.data["province"]
            profile.address = self.request.data["address"]
            profile.avatar = self.request.data["avatar"]
            with transaction.atomic():
                user.save()
                profile.save()
            return Response({"status": "Done"})
        except KeyError as err:
            return Response(
                {
                    "status": "Error",
                    "detail": ErrorResponse.NOT_ENOUGH_DATA,
                    "field:": err,
                },
                status=400,
            )


class FollowEmployee(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FollowSerializer

    def get_employee_profile(self):
        return get_object_or_404(
            EmployeeProfile, id=self.request.data["employee_id"]
        )

    def get_user_profile(self):
        return UserProfile.objects.get(user=self.request.user)

    def post(self, request):
        profile = self.get_user_profile()
        employee = self.get_employee_profile()
        if employee in profile.following.all():
            profile.following.remove(employee)
            profile.save()
            return Response(
                {"status": "Error", "detail": ErrorResponse.FOLLOWING_BEFORE},
                status=400,
            )
        profile.following.add(employee)
        profile.save()
        return Response({"status": "Done"})

    def delete(self, request):
        profile = self.get_user_profile()
        employee = self.get_employee_profile()
        if employee in profile.following.all():
            profile.following.remove(employee)
            profile.save()
            return Response({"status": "Done"})
        return Response(
            {"status": "Error", "detail": ErrorResponse.DID_NOT_FOLLOW},
            status=400,
        )
