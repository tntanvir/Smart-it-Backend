from django.urls import path
from .views import (
    TicketListCreateView, TicketDetailView,
    TicketReviewView, CustomerPaymentRequestsView,
    TechnicianReviewsView
)

urlpatterns = [
    path('', TicketListCreateView.as_view(), name='ticket-list-create'),
    path('payment-requests/', CustomerPaymentRequestsView.as_view(), name='ticket-payment-requests'),
    path('technician-reviews/', TechnicianReviewsView.as_view(), name='technician-reviews'),
    path('<int:pk>/', TicketDetailView.as_view(), name='ticket-detail'),
    path('<int:pk>/review/', TicketReviewView.as_view(), name='ticket-review'),
]
