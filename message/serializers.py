from rest_framework import serializers
from message.models import (
    Message,
    Thread
)

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message

class ThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thread