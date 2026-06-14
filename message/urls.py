from django.urls import path
from .views import TicketChatHistoryView

urlpatterns = [
    path('ticket/<int:pk>/', TicketChatHistoryView.as_view(), name='ticket-chat-history'),
]
