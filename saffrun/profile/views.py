import json

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from profile.models import EmployeeProfile, UserProfile
from rest_framework.views import APIView


# Create your views here.

# class GetEmployeeInfo(API)

class UserView(APIView):
    permission_classes = (AllowAny, IsAuthenticated)

    def get(self, request, *args, **kwargs):
        profile = UserProfile.objects.get(user=request.user)
        return Response(json.dumps({
            'username': request.user.username,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'phone': profile.phone,
            'country': profile.country,
            'province': profile.province,
            'address': profile.address
        }))

    def put(self, request, *args, **kwargs):
        user = request.user
        profile = UserProfile.objects.get(user=request.user)
        try:
            user.username = request.data['username']
            user.first_name = request.data['first_name']
            user.last_name = request.data['last_name']
            user.email = request.data['email']
            profile.phone = request.data['phone']
            profile.country = request.data['country']
            profile.province = request.data['province']
            profile.address = request.data['address']
            profile.avatar = request.data['avatar']
            user.set_password(request.data['password'])
            user.save()
            profile.save()
            return Response(json.dumps({'status': 'Done'}))
        except KeyError as err:
            return Response(json.dumps({'status': 'Error', 'description': f'Not enough data = {err}'}))
