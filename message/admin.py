from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import ChatMessage

@admin.register(ChatMessage)
class ChatMessageAdmin(ModelAdmin):
    list_display = ('ticket', 'sender', 'message', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('message', 'sender__name', 'ticket__title')
