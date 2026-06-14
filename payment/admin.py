from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(ModelAdmin):
    list_display = ('ticket', 'amount', 'status', 'stripe_checkout_session_id', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('ticket__title', 'stripe_checkout_session_id')
