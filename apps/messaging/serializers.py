"""
Serializers for messaging app
"""
from rest_framework import serializers
from .models import Conversation, Message
from django.contrib.auth import get_user_model

User = get_user_model()


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model"""
    
    sender_email = serializers.EmailField(source='sender.email', read_only=True)
    sender_name = serializers.CharField(source='sender.profile.display_name', read_only=True)
    
    class Meta:
        model = Message
        fields = ('id', 'sender', 'sender_email', 'sender_name', 'content', 'is_read', 'created_at')
        read_only_fields = ('id', 'sender', 'created_at')


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for Conversation model"""
    
    participants = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ('id', 'participants', 'job_context', 'last_message', 'unread_count', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def get_participants(self, obj):
        """Get participant details"""
        return [
            {
                'id': user.id,
                'email': user.email,
                'display_name': user.profile.display_name if hasattr(user, 'profile') else user.email
            }
            for user in obj.participants.all()
        ]
    
    def get_last_message(self, obj):
        """Get last message in conversation"""
        last_message = obj.messages.last()
        if last_message:
            return MessageSerializer(last_message).data
        return None
    
    def get_unread_count(self, obj):
        """Get unread message count for current user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.messages.filter(is_read=False).exclude(sender=request.user).count()
        return 0


class ConversationCreateSerializer(serializers.Serializer):
    """Serializer for creating a new conversation"""
    
    recipient_id = serializers.IntegerField(required=True)
    job_id = serializers.IntegerField(required=False, allow_null=True)
    initial_message = serializers.CharField(required=False, allow_blank=True)
