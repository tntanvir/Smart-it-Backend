from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'ticket', 'stripe_checkout_session_id', 'amount', 'status', 'created_at']
        read_only_fields = ['id', 'ticket', 'stripe_checkout_session_id', 'amount', 'status', 'created_at']

class TicketBasicSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    category = serializers.CharField()
    status = serializers.CharField()

class PaymentHistorySerializer(serializers.ModelSerializer):
    ticket_details = TicketBasicSerializer(source='ticket', read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'ticket', 'ticket_details', 'stripe_checkout_session_id', 'amount', 'status', 'created_at']
        read_only_fields = ['id', 'ticket', 'ticket_details', 'stripe_checkout_session_id', 'amount', 'status', 'created_at']
