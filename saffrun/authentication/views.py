import json

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics
from authentication.serializers import RegisterSerializer
from rest_framework.response import Response

from profile.models import Employee, UserProfile


class RegisterUser(generics.CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def __init__(self, ):
        super().__init__()
        self.client_type = None

    def post(self, request, *args, **kwargs):
        client_type = request.headers.get('Client', None)
        if client_type is None:
            return Response(json.dumps({'error': 'No Client field in header found.'}), status=400)
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        user = serializer.save()
        if self.client_type == 'web':
            Employee.object.create(user=user)
        else:
            UserProfile.object.create(user=user)
        return super().perform_create(serializer)

