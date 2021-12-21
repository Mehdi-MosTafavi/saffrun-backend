from event.models import Event
from profile.models import EmployeeProfile

from .models import Comment


def save_a_comment(validated_data: map, user):
    if "event_id" in validated_data:
        event = Event.objects.get(id=validated_data["event_id"])
        comment = Comment.objects.create(
            content=validated_data["content"],
            is_parent=True,
            event=event,
            user=user
        )
        return comment

    elif "owner_id" in validated_data:
        profile = EmployeeProfile.objects.get(id=validated_data["owner_id"])
        comment = Comment.objects.create(
            content=validated_data["content"],
            is_parent=True,
            owner=profile,
            user=user
        )
        return comment
    else:
        raise Exception("incorrect args")


def save_a_reply(validated_data: map, owner, comment):
    reply_2: Comment = Comment.objects.create(
        content=validated_data["content"],
        is_parent=False,
        owner=comment.owner,
        event=comment.event
    )
    reply_2.save()
    comment.reply = reply_2
    comment.save()


def get_event_comments(event):
    return Comment.objects.filter(event__id=event.id, is_parent=True).order_by('-updated_at')


def get_owner_comments(owner):
    return Comment.objects.filter(owner__id=owner.id, is_parent=True).order_by('-updated_at')
