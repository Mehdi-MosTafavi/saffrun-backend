from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from saffrun.comment.models import Comment


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Event(BaseModel):
    def get_file_path(self, filename):
        return "events-picture/" + self.id + "/" + filename

    title = models.CharField(max_length=200)
    participants = models.ManyToManyField(User, on_delete=models.DO_NOTHING)
    description = models.TextField()
    image = models.ImageField(upload_to=get_file_path, blank=True, null=True)
    discount = models.PositiveIntegerField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    comments = models.ManyToManyField(Comment, on_delete=models.CASCADE)
