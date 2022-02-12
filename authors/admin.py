from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Profile

# Register your models here.

class AdminUser(admin.ModelAdmin):

    fields = ("username", )


class AdminProfile(admin.ModelAdmin):

    fields = ("user", )


admin.site.register(get_user_model(), AdminUser)
admin.site.register(Profile, AdminProfile)
