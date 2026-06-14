from django.urls import path
from .views import CreateCheckoutSessionView, StripeWebhookView, CustomerPaymentHistoryView, TechnicianEarningsHistoryView

urlpatterns = [
    path('checkout/<int:ticket_id>/', CreateCheckoutSessionView.as_view(), name='create-checkout-session'),
    path('webhook/', StripeWebhookView.as_view(), name='stripe-webhook'),
    path('history/customer/', CustomerPaymentHistoryView.as_view(), name='customer-payment-history'),
    path('history/technician/', TechnicianEarningsHistoryView.as_view(), name='technician-earnings-history'),
]
