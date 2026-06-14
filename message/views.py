from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from .models import ChatMessage
from .serializers import ChatMessageSerializer
from tickets.models import Ticket

class TicketChatHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            ticket = Ticket.objects.get(pk=pk)
        except Ticket.DoesNotExist:
            return Response({"error": "Ticket not found"}, status=status.HTTP_404_NOT_FOUND)
            
        # Check permissions
        if ticket.user != request.user and ticket.assigned_technician != request.user:
            return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
            
        # Only allow if ticket is accepted (assigned, in_progress, pending_confirmation, done)
        if ticket.status == 'open':
            return Response({"error": "Chat is not available until a technician accepts the ticket."}, status=status.HTTP_400_BAD_REQUEST)
            
        messages = ticket.chat_messages.all().select_related('sender').order_by('created_at')
        
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(messages, request)
        if page is not None:
            serializer = ChatMessageSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)
