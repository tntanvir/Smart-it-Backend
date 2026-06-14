from django.urls import path
from .views import AvailableTicketsView, AcceptTicketView, TechnicianDashboardView, TicketCompleteView

urlpatterns = [
    path('tickets/available/', AvailableTicketsView.as_view(), name='available-tickets'),
    path('ticket/<int:pk>/accept/', AcceptTicketView.as_view(), name='accept-ticket'),
    path('ticket/<int:pk>/complete/', TicketCompleteView.as_view(), name='complete-ticket'),
    # Requested URL by the user
    path('ticket/accpet/deshboard/', TechnicianDashboardView.as_view(), name='technician-dashboard'),
]
