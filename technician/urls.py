from django.urls import path
from .views import AvailableTicketsView, AcceptTicketView, TechnicianDashboardView, TicketCompleteView, PublicJobsView, PublicJobDetailView

urlpatterns = [
    path('tickets/available/', AvailableTicketsView.as_view(), name='available-tickets'),
    path('public-jobs/', PublicJobsView.as_view(), name='public-jobs'),
    path('public-jobs/<int:pk>/', PublicJobDetailView.as_view(), name='public-job-detail'),
    path('ticket/<int:pk>/accept/', AcceptTicketView.as_view(), name='accept-ticket'),
    path('ticket/<int:pk>/complete/', TicketCompleteView.as_view(), name='complete-ticket'),
    # Requested URL by the user
    path('ticket/accpet/deshboard/', TechnicianDashboardView.as_view(), name='technician-dashboard'),
]
