from rest_framework import serializers
from .models import Ticket, Review
from authsystem.serializers import UserSerializer

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'ticket', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'ticket', 'created_at']

class TicketSerializer(serializers.ModelSerializer):
    # Read-only fields to get detailed user info when reading
    customer_info = UserSerializer(source='user', read_only=True)
    technician_info = UserSerializer(source='assigned_technician', read_only=True)
    review = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = [
            'id', 'user', 'title', 'description', 'category', 'priority',
            'status', 'budget', 'assigned_technician', 'created_at', 'updated_at',
            'customer_info', 'technician_info', 'review'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'status', 'assigned_technician']

    def get_review(self, obj):
        try:
            if obj.review:
                return ReviewSerializer(obj.review).data
        except Exception:
            return None
        return None

    def create(self, validated_data):
        # Automatically set the logged-in user as the creator
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)


