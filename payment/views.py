import os
import stripe
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from tickets.models import Ticket
from .models import Payment

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

class CreateCheckoutSessionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, ticket_id):
        try:
            ticket = Ticket.objects.get(id=ticket_id)
        except Ticket.DoesNotExist:
            return Response({"error": "Ticket not found"}, status=status.HTTP_404_NOT_FOUND)

        if ticket.user != request.user:
            return Response({"error": "Only the ticket owner can initiate payment."}, status=status.HTTP_403_FORBIDDEN)
            
        if ticket.status != 'pending_confirmation':
            return Response({"error": "Ticket is not ready for payment."}, status=status.HTTP_400_BAD_REQUEST)

        # Retrieve budget as the charge amount
        amount = ticket.budget if ticket.budget else 10.00
        # Stripe uses cents for USD
        amount_cents = int(float(amount) * 100)

        domain_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')

        try:
            # Create Stripe Checkout Session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price_data': {
                            'currency': 'usd',
                            'unit_amount': amount_cents,
                            'product_data': {
                                'name': f'Ticket #{ticket.id}: {ticket.title}',
                            },
                        },
                        'quantity': 1,
                    },
                ],
                mode='payment',
                success_url=domain_url.rstrip('/') + '/dashboard/customer/payments?session_id={CHECKOUT_SESSION_ID}&success=true',
                cancel_url=domain_url.rstrip('/') + f'/dashboard/customer/ticket/{ticket.id}?canceled=true',
                client_reference_id=str(ticket.id)
            )

            # Store the payment intent locally
            Payment.objects.update_or_create(
                ticket=ticket,
                defaults={
                    'stripe_checkout_session_id': checkout_session['id'],
                    'amount': amount,
                    'status': 'pending'
                }
            )

            return Response({'checkout_url': checkout_session.url})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class StripeWebhookView(APIView):
    permission_classes = [AllowAny] # Webhooks are public and verified via signature

    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')

        event = None

        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError as e:
            # Invalid payload
            return Response(status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.SignatureVerificationError as e:
            # Invalid signature
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # Handle the checkout.session.completed event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            ticket_id = session.get('client_reference_id')

            if ticket_id:
                try:
                    ticket = Ticket.objects.get(id=ticket_id)
                    payment = Payment.objects.get(ticket=ticket)
                    
                    # Mark payment as completed
                    payment.status = 'completed'
                    payment.save()

                    # Mark ticket as done
                    ticket.status = 'done'
                    ticket.save()
                    
                    # Notify technician about successful payment
                    from authsystem.utils import create_and_send_notification
                    if ticket.assigned_technician:
                        create_and_send_notification(
                            user=ticket.assigned_technician,
                            message=f"Payment received! Ticket #{ticket.id} is now complete.",
                            link="/dashboard/technician/earnings"
                        )
                except (Ticket.DoesNotExist, Payment.DoesNotExist):
                    pass

        return Response(status=status.HTTP_200_OK)

from rest_framework import generics
from django_filters import rest_framework as filters
from .serializers import PaymentHistorySerializer

class PaymentFilter(filters.FilterSet):
    status = filters.ChoiceFilter(choices=Payment.STATUS_CHOICES)
    min_amount = filters.NumberFilter(field_name="amount", lookup_expr='gte')
    max_amount = filters.NumberFilter(field_name="amount", lookup_expr='lte')
    
    class Meta:
        model = Payment
        fields = ['status']

class CustomerPaymentHistoryView(generics.ListAPIView):
    serializer_class = PaymentHistorySerializer
    permission_classes = [IsAuthenticated]
    filterset_class = PaymentFilter

    def get_queryset(self):
        return Payment.objects.filter(ticket__user=self.request.user).order_by('-created_at')

class TechnicianEarningsHistoryView(generics.ListAPIView):
    serializer_class = PaymentHistorySerializer
    permission_classes = [IsAuthenticated]
    filterset_class = PaymentFilter

    def get_queryset(self):
        return Payment.objects.filter(ticket__assigned_technician=self.request.user).order_by('-created_at')
