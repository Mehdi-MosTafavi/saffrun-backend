import json

from django.db import transaction
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from profile.models import EmployeeProfile, UserProfile
from rest_framework.views import APIView


# Create your views here.

# class GetEmployeeInfo(API)

class UserView(APIView):
    permission_classes = (AllowAny, IsAuthenticated)

    def get(self, *args, **kwargs):
        profile = UserProfile.objects.get(user=self.request.user)
        return Response(json.dumps({
            'username': self.request.user.username,
            'first_name': self.request.user.first_name,
            'last_name': self.request.user.last_name,
            'email': self.request.user.email,
            'phone': profile.phone,
            'country': profile.country,
            'province': profile.province,
            'address': profile.address
        }))

    def put(self, *args, **kwargs):
        user = self.request.user
        profile = UserProfile.objects.get(user=user)
        try:
            user.username = self.request.data['username']
            user.first_name = self.request.data['first_name']
            user.last_name = self.request.data['last_name']
            user.email = self.request.data['email']
            profile.phone = self.request.data['phone']
            profile.country = self.request.data['country']
            profile.province = self.request.data['province']
            profile.address = self.request.data['address']
            profile.avatar = self.request.data['avatar']
            with transaction.atomic():
                user.save()
                profile.save()
            return Response(json.dumps({'status': 'Done'}))
        except KeyError as err:
            return Response(json.dumps({'status': 'Error', 'detail': f'Not enough data = {err}'}))


class FollowEmployee(APIView):
    permission_classes = (IsAuthenticated,)

    def get_employee_profile(self):
        return get_object_or_404(EmployeeProfile, id=self.request.data['employee_id'])

    def get_user_profile(self):
        return UserProfile.objects.get(user=self.request.user)

    def post(self, *args, **kwargs):
        profile = self.get_user_profile()
        employee = self.get_employee_profile()
        if employee in profile.following.all():
            profile.following.remove(employee)
            profile.save()
            return Response(json.dumps({'status': 'Error', 'detail': 'Following before'}), status=400)
        profile.following.add(employee)
        profile.save()
        return Response(json.dumps({'status': 'Done'}))

    def delete(self, *args, **kwargs):
        profile = self.get_user_profile()
        employee = self.get_employee_profile()
        if employee in profile.following.all():
            profile.following.remove(employee)
            profile.save()
            return Response(json.dumps({'status': 'Done'}))
        return Response(json.dumps({'status': 'Error', 'detail': 'Did not following'}), status=400)
