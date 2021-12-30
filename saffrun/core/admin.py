from django.contrib import admin

# Register your models here.
from .models import Image, Business

admin.site.register(Image)
admin.site.register(Business)
