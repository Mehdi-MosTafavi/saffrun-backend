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

    def get_profile(self):
        try:
            profile = EmployeeProfile.objects.get(user=self.request.user)
        except EmployeeProfile.DoesNotExist:
            profile = UserProfile.objects.get(user=self.request.user)
        if profile is None:
            raise Exception('No profile Found!')
        return profile

    def get(self, request):
        try:
            profile = self.get_profile()
        except KeyError as err:
            return Response(
                {"status": "Error", "detail": ErrorResponse.NOT_PROFILE_FOUND},
                status=400,
            )
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
            profile = self.get_profile()
        except KeyError as err:
            return Response(
                {"status": "Error", "detail": ErrorResponse.NOT_PROFILE_FOUND},
                status=400,
            )
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
                    "field:": str(err),
                },
                status=400,
            )


class FollowEmployee(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = FollowSerializer

    def _get_employee_profile(self):
        return get_object_or_404(EmployeeProfile, id=self.request.data["employee_id"])

    def _get_user_profile(self):
        return get_object_or_404(UserProfile, user=self.request.user)

    def get(self, request):
        profile:EmployeeProfile = get_object_or_404(EmployeeProfile, user=self.request.user)
        followers = profile.followers.all()
        follwers_list = []
        for index, follower in enumerate(followers):
            follwers_list.append({'username': follower.user.username,
                                      'email': follower.user.email,
                                      'city': follower.city,
                                      'avatar': follower.avatar})
        return Response(follwers_list)

    def post(self, request):
        profile = self._get_user_profile()
        employee = self._get_employee_profile()
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
        profile = self._get_user_profile()
        employee = self._get_employee_profile()
        if employee in profile.following.all():
            profile.following.remove(employee)
            profile.save()
            return Response({"status": "Done"})
        return Response(
            {"status": "Error", "detail": ErrorResponse.DID_NOT_FOLLOW},
            status=400,
        )
