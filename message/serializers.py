from rest_framework import serializers
from .models import ChatMessage
from authsystem.serializers import UserSerializer

class ChatMessageSerializer(serializers.ModelSerializer):
    sender_info = UserSerializer(source='sender', read_only=True)

    class Meta:
        model = ChatMessage
        fields = ['id', 'ticket', 'sender', 'message', 'created_at', 'sender_info']
        read_only_fields = ['id', 'ticket', 'sender', 'created_at']
