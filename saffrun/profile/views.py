from core.models import Image
from core.responses import ErrorResponse
# Create your views here.
from core.responses import SuccessResponse
from core.serializers import ImageAvatarSerializer
from django.db import transaction
from django.db.models import F
from drf_yasg.utils import swagger_auto_schema
from profile.models import EmployeeProfile, UserProfile
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404, GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import FollowSerializer, RemoveFollowerSerializer
from .utils import remove_follower_user


class UserView(APIView):
    permission_classes = (AllowAny, IsAuthenticated)

    def _get_profile(self):
        try:
            profile = EmployeeProfile.objects.get(user=self.request.user)
        except:
            try:
                profile = UserProfile.objects.get(user=self.request.user)
            except:
                profile = None
        if profile is None:
            raise Exception('No profile Found!')
        return profile

    def get(self, request):
        try:
            profile = self._get_profile()
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
                "gender": profile.gender,
                "category": {
                    'id': profile.category.id,
                    'title': profile.category.name
                } if isinstance(profile, EmployeeProfile) else {},
                "address": profile.address,
                "avatar": ImageAvatarSerializer(instance=profile.avatar).data
            }
        )

    def put(self, request):
        user = self.request.user
        try:
            profile = self._get_profile()
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
            profile.gender = self.request.data["gender"]
            if "image_id" in self.request.data:
                if self.request.data["image_id"] == -1:
                    profile.avatar = None
                else:
                    profile.avatar = get_object_or_404(Image, id=self.request.data["image_id"])
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
        profile: EmployeeProfile = get_object_or_404(EmployeeProfile, user=self.request.user)
        followers = profile.followers.values('id', 'city', 'avatar', username=F('user__username'),
                                             email=F('user__email'))
        for index in range(len(followers)):
            if followers[index]["avatar"] is None:
                followers[index]["avatar"] = {'image': None}
            else:
                followers[index]["avatar"] = ImageAvatarSerializer(
                    instance=get_object_or_404(Image, id=followers[index]['avatar'])).data

        return Response(followers)

    def post(self, request):
        profile = self._get_user_profile()
        employee = self._get_employee_profile()
        if employee in profile.following.all():
            profile.following.remove(employee)
            profile.save()
            return Response({"status": "Done Remove"})

        profile.following.add(employee)
        profile.save()
        return Response({"status": "Done"})

    def delete(self, request, employee_id=None):
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


@swagger_auto_schema(
    method="DELETE",
    request_body=RemoveFollowerSerializer,
    responses={
        201: SuccessResponse.DELETED,
        406: ErrorResponse.INVALID_DATA,
    },
)
@api_view(["DELETE"])
def remove_follower(request):
    follower_serializer = RemoveFollowerSerializer(data=request.data)
    if not follower_serializer.is_valid():
        return Response(
            {"Error": ErrorResponse.INVALID_DATA},
            status=status.HTTP_406_NOT_ACCEPTABLE,
        )
    employee = get_object_or_404(EmployeeProfile, user=request.user)
    user = get_object_or_404(UserProfile, id=follower_serializer.validated_data['user_id'])
    if user in employee.followers.all():
        remove_follower_user(user, employee)
        return Response(
            {"success": SuccessResponse.DELETED}, status=status.HTTP_200_OK
        )
    return Response(
        {"status": "Error", "detail": ErrorResponse.DID_NOT_FOLLOW},
        status=status.HTTP_400_BAD_REQUEST,
    )
