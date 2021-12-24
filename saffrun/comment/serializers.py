from rest_flex_fields import FlexFieldsModelSerializer
from rest_framework import serializers

from .models import Comment
from core.serializers import ImageAvatarSerializer


class ReplyRelatedField(serializers.RelatedField):
    """
    A custom field to use for the 'tagged_object' generic relationship
    """

    def to_representation(self, value):
        """
        Serialize tagged objects to their respective serializer formats
        :param value:
        :return:
            serializer.data
        """
        if isinstance(value, Comment):
            return {
                'id': value.id,
                'content': value.content,
                'time': value.updated_at,
                "owner": value.event.owner.user.username if value.owner is None else value.owner.user.username,
                "image": ImageAvatarSerializer(instance=value.event.owner.avatar if value.owner is None else value.owner.avatar).data
            }
        raise Exception('Unexpected type of tagged object')


class CommentSerializer(FlexFieldsModelSerializer):
    reply = ReplyRelatedField(queryset=Comment.objects.all())
    user = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ["id",
                  "content",
                  'user',
                  'reply',
                  "created_at",
                  ]

    def get_user(self, obj: Comment):
        return {"name": obj.user.user.last_name, "image": ImageAvatarSerializer(instance=obj.user.avatar).data}


class CommentPostSerializer(serializers.Serializer):
    owner_id = serializers.IntegerField(allow_null=True, required=False)
    event_id = serializers.IntegerField(allow_null=True, required=False)
    content = serializers.CharField()


class ReplyPostSerializer(serializers.Serializer):
    comment_id = serializers.IntegerField()
    content = serializers.CharField()


class ManyCommentSerializer(serializers.Serializer):
    comments = CommentSerializer(many=True)


class AllCommentSerializer(serializers.Serializer):
    search_query = serializers.CharField(
        max_length=200, allow_null=False, allow_blank=True
    )


class EventCommentSerializer(serializers.Serializer):
    event_id = serializers.IntegerField()


class AdminCommentSerializer(serializers.Serializer):
    admin_id = serializers.IntegerField()
