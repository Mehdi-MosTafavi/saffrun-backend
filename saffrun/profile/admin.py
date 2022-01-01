from django.contrib import admin
from profile.models import Business
# Register your models here.
from profile.models import EmployeeProfile, UserProfile

admin.site.register(EmployeeProfile)
admin.site.register(UserProfile)
admin.site.register(Business)
