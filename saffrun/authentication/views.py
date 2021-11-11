import json

from django.db import transaction
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
        self.client_type = request.headers.get('Client', None)
        if self.client_type is None:
            return Response(json.dumps({'error': 'No Client field in header found.'}), status=400)
        return super().post(request, *args, **kwargs)
    
    def finalize_response(self, request, response, *args, **kwargs):
        print(response.__dict__)
        response.data = {'status': 'okay'}
        return super(RegisterUser, self).finalize_response(request, response, *args, **kwargs)
    
    def perform_create(self, serializer):
        if not serializer.is_valid():
            raise
        user = serializer.create_instance()
        profile = None
        if self.client_type == 'web':
            profile = Employee(user=user)
        elif self.client_type == 'app':
            profile = UserProfile(user=user)
        print(serializer.__dict__)
        with transaction.atomic():
            user.save()
            profile.save()
            return

