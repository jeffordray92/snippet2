from django.contrib import admin
from user_profile.models import Preference, UserProfile


admin.site.register(UserProfile)
admin.site.register(Preference)