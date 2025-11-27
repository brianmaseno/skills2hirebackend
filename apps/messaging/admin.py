"""
Admin configuration for messaging app
"""
from django.contrib import admin
from .models import Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """Admin configuration for Conversation model"""
    
    list_display = ('id', 'get_participants', 'job_context', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('participants__email',)
    readonly_fields = ('created_at', 'updated_at')
    
    def get_participants(self, obj):
        return ', '.join([p.email for p in obj.participants.all()])
    get_participants.short_description = 'Participants'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """Admin configuration for Message model"""
    
    list_display = ('id', 'sender', 'conversation', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('sender__email', 'content')
    readonly_fields = ('created_at',)
