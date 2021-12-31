from django.contrib.auth.models import User
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from core.responses import SuccessResponse


def change_password(username: str, old_password: str, new_password: str) -> Response:
    user = get_object_or_404(User, username=username)
    if not user.check_password(old_password):
        return Response({
            "status": "error",
            "detail": "Wrong old password"
        }, status=400)
    user.set_password(new_password)
    user.save()
    return Response({
        "status": "success",
        "detail": SuccessResponse.CHANGED
    }, status=200)