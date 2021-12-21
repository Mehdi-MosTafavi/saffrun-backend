from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import RetrieveUpdateDestroyAPIView, CreateAPIView
from rest_framework.response import Response

from core.responses import ErrorResponse, SuccessResponse

# Create your views here.
from drf_yasg.utils import swagger_auto_schema

from comment.models import Comment
from comment.serializers import CommentSerializer, AllCommentSerializer, ManyCommentSerializer, \
    CommentPostSerializer, ReplyPostSerializer
from comment.utils import save_a_comment, save_a_reply, get_event_comments, get_owner_comments
from core.responses import SuccessResponse
from event.models import Event

from comment.serializers import EventCommentSerializer

from comment.serializers import AdminCommentSerializer

from profile.models import EmployeeProfile


@swagger_auto_schema(
    method="post",
    request_body=CommentPostSerializer,
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
    comment = save_a_comment(
        comment_serializer.validated_data, request.user.user_profile
    )
    return Response(
        {"success": SuccessResponse.CREATED,"comment" : CommentSerializer(instance=comment).data}, status=status.HTTP_201_CREATED
    )


@swagger_auto_schema(
    method="post",
    request_body=ReplyPostSerializer,
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
    comment:Comment = Comment.objects.get(id=reply_serializer.validated_data["comment_id"])
    if not comment.is_parent:
        return Response(
            {"Error": ErrorResponse.INVALID_DATA},
            status=status.HTTP_406_NOT_ACCEPTABLE,
        )
    if comment.reply is not None:
        return Response(
            {"Error": ErrorResponse.INVALID_DATA},
            status=status.HTTP_406_NOT_ACCEPTABLE,
        )
    save_a_reply(
        reply_serializer.validated_data, request.user.employee_profile, comment
    )
    return Response(
        {"success": SuccessResponse.CREATED}, status=status.HTTP_201_CREATED
    )


@swagger_auto_schema(
    method="get",
    query_serializer=EventCommentSerializer,
    responses={200: ManyCommentSerializer, 406: ErrorResponse.INVALID_DATA},
)
@api_view(["GET"])
def get_all_event_comments(request):
    event_serializer = EventCommentSerializer(data=request.GET)
    if not event_serializer.is_valid():
        return Response(
            {"Error": ErrorResponse.INVALID_DATA},
            status=status.HTTP_406_NOT_ACCEPTABLE,
        )
    event = Event.objects.get(id=event_serializer.validated_data["event_id"])
    comments = get_event_comments(event)
    return Response(
        {"comments": CommentSerializer(instance=comments, many=True).data},
        status=status.HTTP_200_OK,
    )


@swagger_auto_schema(
    method="get",
    query_serializer=AdminCommentSerializer,
    responses={200: ManyCommentSerializer, 406: ErrorResponse.INVALID_DATA},
)
@api_view(["GET"])
def get_all_owner_comments(request):
    admin_serializer = AdminCommentSerializer(data=request.GET)
    if not admin_serializer.is_valid():
        return Response(
            {"Error": ErrorResponse.INVALID_DATA},
            status=status.HTTP_406_NOT_ACCEPTABLE,
        )
    owner = EmployeeProfile.objects.get(id=admin_serializer.validated_data['admin_id'])
    comments = get_owner_comments(owner)
    return Response(
        {"comments": CommentSerializer(instance=comments, many=True).data},
        status=status.HTTP_200_OK,
    )
@swagger_auto_schema(
    method="get",
    responses={200: CommentSerializer, 406: ErrorResponse.INVALID_DATA},
)
@api_view(["GET"])
def get_comment_of_owner(request):
    owner = EmployeeProfile.objects.get(user=request.user)
    comments = get_owner_comments(owner)
    return Response(
        {"comments": CommentSerializer(instance=comments, many=True).data},
        status=status.HTTP_200_OK,
    )