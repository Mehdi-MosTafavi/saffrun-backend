from django.contrib import admin

# Register your models here.
from profile.models import Employee, UserProfile

admin.site.register(Employee)
admin.site.register(UserProfile)