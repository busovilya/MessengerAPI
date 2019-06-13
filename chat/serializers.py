from rest_framework import serializers

from chat.models import Message, Chat
from profiles.serializers import UserSerializer


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('sender', 'text', 'chat', 'time', 'is_edited')


class ChatSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True)

    class Meta:
        model = Chat
        fields = ('participants', 'is_private')

