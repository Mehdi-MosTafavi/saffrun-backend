from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import RetrieveUpdateDestroyAPIView, CreateAPIView
from rest_framework.response import Response

from core.responses import ErrorResponse, SuccessResponse

# Create your views here.
from drf_yasg.utils import swagger_auto_schema

from saffrun.comment.models import Comment
from saffrun.comment.serializers import CommentSerializer, AllCommentSerializer, ManyCommentSerializer, \
    CommentPostSerializer, ReplyPostSerializer
from saffrun.comment.utils import save_a_comment, save_a_reply, get_event_comments, get_owner_comments
from saffrun.core.responses import SuccessResponse
from saffrun.event.models import Event


@swagger_auto_schema(
    method="post",
    request_body=CommentSerializer,
    responses={
        201: SuccessResponse.CREATED,
        406: ErrorResponse.INVALID_DATA,
    },
)
@api_view(["POST"])
def save_comment(request):
    comment_serializer = CommentPostSerializer(data=request.data)
    if not comment_serializer.is_valid():
        return Response(
            {"Error": ErrorResponse.INVALID_DATA},
            status=status.HTTP_406_NOT_ACCEPTABLE,
        )
    save_a_comment(
        comment_serializer.validated_data, request.user.user_profile
    )
    return Response(
        {"success": SuccessResponse.CREATED}, status=status.HTTP_201_CREATED
    )


@swagger_auto_schema(
    method="post",
    request_body=CommentSerializer,
    responses={
        201: SuccessResponse.CREATED,
        406: ErrorResponse.INVALID_DATA,
    },
)
@api_view(["POST"])
def save_reply(request):
    reply_serializer = ReplyPostSerializer(data=request.data)
    if not reply_serializer.is_valid():
        return Response(
            {"Error": ErrorResponse.INVALID_DATA},
            status=status.HTTP_406_NOT_ACCEPTABLE,
        )
    comment = Comment.objects.get(id=reply_serializer.validated_data["id"])
    save_a_reply(
        reply_serializer.validated_data, request.user.employee_profile, comment
    )
    return Response(
        {"success": SuccessResponse.CREATED}, status=status.HTTP_201_CREATED
    )


@swagger_auto_schema(
    method="get",
    query_serializer=AllCommentSerializer,
    responses={200: ManyCommentSerializer, 406: ErrorResponse.INVALID_DATA},
)
@api_view(["GET"])
def get_all_event_comments(request):
    event = Event.objects.get(id=request.data["event_id"])
    comments = get_event_comments(event)
    return Response(
        {"comments": CommentSerializer(instance=comments, many=True).data},
        status=status.HTTP_200_OK,
    )


@swagger_auto_schema(
    method="get",
    query_serializer=AllCommentSerializer,
    responses={200: ManyCommentSerializer, 406: ErrorResponse.INVALID_DATA},
)
@api_view(["GET"])
def get_all_owner_comments(request):
    owner = Event.objects.get(id=request.data["owner_id"])
    comments = get_owner_comments(owner)
    return Response(
        {"comments": CommentSerializer(instance=comments, many=True).data},
        status=status.HTTP_200_OK,
    )