from rest_framework import serializers

from .models import Comment


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
                'time': value.updated_at
            }
        raise Exception('Unexpected type of tagged object')


class CommentSerializer(serializers.ModelSerializer):
    reply = ReplyRelatedField(queryset=Comment.objects.all())

    class Meta:
        model = Comment
        fields = ["id",
                  "content",
                  'reply',
                  "created_at",
                  ]


class CommentPostSerializer(serializers.Serializer):
    owner_id = serializers.IntegerField(allow_null=True,required=False)
    event_id = serializers.IntegerField(allow_null=True,required=False)
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
