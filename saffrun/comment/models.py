# Create your models here.
from core.models import BaseModel
from django.db import models
from event.models import Event
from profile.models import UserProfile, EmployeeProfile


class CommentManager(models.Manager):
    def get_queryset(self):
        return super(CommentManager, self).get_queryset().filter(is_active=True)


class Comment(BaseModel):
    is_parent = models.BooleanField()
    content = models.CharField(max_length=200)
    user = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="comment_writer", null=True, blank=True
    )
    owner = models.ForeignKey(
        EmployeeProfile, on_delete=models.CASCADE, related_name="comment_owner", null=True, blank=True
    )
    event = models.ForeignKey(
        Event, on_delete=models.CASCADE, related_name="comment_event", null=True, blank=True
    )
    reply = models.OneToOneField(
        'self', on_delete=models.CASCADE, related_name="replied_comment", null=True, blank=True,
        unique=True, db_index=True
    )
    objects = CommentManager()
