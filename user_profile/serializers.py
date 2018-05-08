from django.contrib.auth.models import User

from rest_framework import serializers
from item.serializer_fields import Base64ImageField
from user_profile.models import (
    Preference,
    UserProfile
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'username', 'password')

class UserProfileSerializer(serializers.ModelSerializer):
    photo = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = UserProfile

class PreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Preference
