from django.contrib import admin

# Register your models here.
from profile.models import EmployeeProfile, UserProfile

admin.site.register(EmployeeProfile)
admin.site.register(UserProfile)