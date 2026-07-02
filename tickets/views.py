from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from .models import Ticket, Category
from .serializers import TicketSerializer, CategorySerializer

class CategoryListView(APIView):
    permission_classes = [] # Publicly accessible
    
    def get(self, request):
        categories = Category.objects.all().prefetch_related('subcategories')
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TicketListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role == 'technician':
            # Technicians can see all open tickets and tickets assigned to them
            open_tickets = Ticket.objects.filter(status='open').select_related('user', 'assigned_technician')
            assigned_tickets = Ticket.objects.filter(assigned_technician=request.user).select_related('user', 'assigned_technician')
            tickets = (open_tickets | assigned_tickets).distinct().order_by('-created_at')
        else:
            # Customers see their own tickets
            tickets = Ticket.objects.filter(user=request.user).select_related('user', 'assigned_technician').order_by('-created_at')
            
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(tickets, request)
        if page is not None:
            serializer = TicketSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = TicketSerializer(tickets, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.user.role != 'customer':
            return Response({"error": "Only customers can create tickets."}, status=status.HTTP_403_FORBIDDEN)
            
        serializer = TicketSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            ticket = serializer.save()
            
            # Notify all technicians
            from authsystem.utils import create_and_send_notification
            from authsystem.models import User
            technicians = User.objects.filter(role='technician', is_active=True)
            for tech in technicians:
                create_and_send_notification(
                    user=tech,
                    message=f"New ticket posted: '{ticket.title}'",
                    link="/dashboard/technician"
                )
                
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TicketDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            ticket = Ticket.objects.get(pk=pk)
            # Check permissions
            if user.role == 'customer' and ticket.user != user:
                return None
            return ticket
        except Ticket.DoesNotExist:
            return None

    def get(self, request, pk):
        ticket = self.get_object(pk, request.user)
        if not ticket:
            return Response({"error": "Not found or permission denied."}, status=status.HTTP_404_NOT_FOUND)
            
        serializer = TicketSerializer(ticket)
        return Response(serializer.data)

    def put(self, request, pk):
        # We will allow PUT and PATCH
        ticket = self.get_object(pk, request.user)
        if not ticket:
            return Response({"error": "Not found or permission denied."}, status=status.HTTP_404_NOT_FOUND)
            
        if request.user.role != 'customer' or ticket.user != request.user:
            return Response({"error": "You do not have permission to edit this ticket."}, status=status.HTTP_403_FORBIDDEN)

        serializer = TicketSerializer(ticket, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        return self.put(request, pk)

    def delete(self, request, pk):
        ticket = self.get_object(pk, request.user)
        if not ticket:
            return Response({"error": "Not found or permission denied."}, status=status.HTTP_404_NOT_FOUND)
            
        if request.user.role != 'customer' or ticket.user != request.user:
            return Response({"error": "You do not have permission to delete this ticket."}, status=status.HTTP_403_FORBIDDEN)

        ticket.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

from .models import Review
from .serializers import ReviewSerializer, TopReviewSerializer
from django.db.models import Avg

class TopReviewsView(APIView):
    permission_classes = [] # Allow unauthenticated access for homepage

    def get(self, request):
        reviews = Review.objects.select_related(
            'ticket', 'ticket__user', 'ticket__assigned_technician'
        ).order_by('-rating', '-created_at')[:15]
        
        serializer = TopReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

from django.core.mail import EmailMessage
from django.conf import settings

class SupportMessageView(APIView):
    permission_classes = [] # Allow unauthenticated access

    def post(self, request):
        subject = request.data.get('subject')
        body = request.data.get('body')
        
        if request.user.is_authenticated:
            email = request.user.email
        else:
            email = request.data.get('email')
            
        if not subject or not body or not email:
            return Response({'error': 'Subject, body, and email are required.'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            # 1. Send to Admin
            admin_msg = EmailMessage(
                subject=f"New Support Request: {subject}",
                body=f"You have received a new support request.\n\nFrom: {email}\n\nMessage:\n{body}",
                from_email=settings.EMAIL_HOST_USER,
                to=[settings.EMAIL_HOST_USER],
                reply_to=[email],
            )
            admin_msg.send(fail_silently=False)
            
            # 2. Send Auto-reply to User
            user_msg = EmailMessage(
                subject=f"Re: Support Request: {subject}",
                body=f"Hi there,\n\nWe have received your support request regarding '{subject}'. Our team will review it and get back to you shortly.\n\nYour message:\n{body}\n\nThanks,\nTechBridge Support Team",
                from_email=settings.EMAIL_HOST_USER,
                to=[email],
            )
            user_msg.send(fail_silently=False)
            
            return Response({'message': 'Support message sent successfully.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TicketReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            ticket = Ticket.objects.get(pk=pk)
        except Ticket.DoesNotExist:
            return Response({"error": "Ticket not found"}, status=status.HTTP_404_NOT_FOUND)
            
        if ticket.user != request.user:
            return Response({"error": "Only the customer can leave a review."}, status=status.HTTP_403_FORBIDDEN)
            
        if ticket.status != 'done':
            return Response({"error": "Ticket must be completed and confirmed before reviewing."}, status=status.HTTP_400_BAD_REQUEST)
            
        serializer = ReviewSerializer(data=request.data)
        if serializer.is_valid():
            review = serializer.save(ticket=ticket)
            
            # Recalculate technician rating
            tech = ticket.assigned_technician
            if tech and hasattr(tech, 'technician_profile'):
                profile = tech.technician_profile
                # calculate avg rating from all reviews for this technician
                avg_rating = Review.objects.filter(ticket__assigned_technician=tech).aggregate(Avg('rating'))['rating__avg']
                profile.rating = avg_rating
                profile.save()
                
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomerPaymentRequestsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'customer':
            return Response({"error": "Only customers can view payment requests."}, status=status.HTTP_403_FORBIDDEN)
            
        tickets = Ticket.objects.filter(user=request.user, status='pending_confirmation').select_related('user', 'assigned_technician').order_by('-updated_at')
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(tickets, request)
        if page is not None:
            serializer = TicketSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = TicketSerializer(tickets, many=True)
        return Response(serializer.data)

class TechnicianReviewsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'technician':
            return Response({"error": "Only technicians can view their reviews."}, status=status.HTTP_403_FORBIDDEN)
            
        reviews = Review.objects.filter(ticket__assigned_technician=request.user).order_by('-created_at')
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
