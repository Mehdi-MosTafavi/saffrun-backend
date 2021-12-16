from django.db.models import Q

from .models import Comment
from ..event.models import Event
from ..profile.models import EmployeeProfile


def save_a_comment(validated_data: map, user):
    if "event_id" in validated_data:
        event = Event.objects.get(id=validated_data["event_id"])
        Comment.objects.create(
            content=validated_data["content"],
            is_parent=True,
            event=event,
            user=user
        )
    elif "owner_id" in validated_data:
        profile = EmployeeProfile.objects.get(id=validated_data["owner_id"])
        Comment.objects.create(
            content=validated_data["content"],
            is_parent=True,
            owner=profile,
            user=user
        )
    else:
        raise Exception("incorrect args")


def save_a_reply(validated_data: map, owner, comment):
    reply = Comment.objects.create(
        content=validated_data["content"],
        is_parent=False,
        owner=comment.owner,
        event=comment.event
    )
    comment.reply=reply
    comment.save()


def get_event_comments(event):
    return Comment.objects.filter(event__id=event.id, is_parent=True).order_by('-updated_at')


def get_owner_comments(owner):
    return Comment.objects.filter(owner__id=owner.id, is_parent=True).order_by('-updated_at')
