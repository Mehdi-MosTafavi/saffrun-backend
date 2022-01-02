from core.responses import SuccessResponse
from django.contrib.auth.models import User
from rest_framework.response import Response


def change_password(user: User, old_password: str, new_password: str) -> Response:
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