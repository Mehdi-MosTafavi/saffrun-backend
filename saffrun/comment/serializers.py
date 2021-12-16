from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from rest_framework import serializers, status
from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework.response import Response

from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id",
                  "content",
                  "reply",
                  "created_at",
                  ]


class CommentPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["content",
                  "owner_id",
                  "event_id",
                  ]


class ReplyPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id",
                  "content",
                  ]


class ManyCommentSerializer(serializers.Serializer):
    comments = CommentSerializer(many=True)


class AllCommentSerializer(serializers.Serializer):
    search_query = serializers.CharField(
        max_length=200, allow_null=False, allow_blank=True
    )


