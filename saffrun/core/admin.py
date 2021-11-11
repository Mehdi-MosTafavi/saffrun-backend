from django.contrib import admin

# Register your models here.
from .models import Comment, Image

admin.site.register(Comment)
admin.site.register(Image)
