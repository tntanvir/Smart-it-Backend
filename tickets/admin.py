from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Ticket, Review

@admin.register(Ticket)
class TicketAdmin(ModelAdmin):
    list_display = ('title', 'user', 'category', 'priority', 'status', 'budget', 'assigned_technician', 'created_at')
    list_filter = ('status', 'priority', 'category')
    search_fields = ('title', 'description', 'user__name', 'user__email')

@admin.register(Review)
class ReviewAdmin(ModelAdmin):
    list_display = ('ticket', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('ticket__title', 'comment')
