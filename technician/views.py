from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from tickets.models import Ticket
from tickets.serializers import TicketSerializer
from rest_framework.pagination import PageNumberPagination

class AvailableTicketsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'technician':
            return Response({"error": "Only technicians can view available tickets."}, status=status.HTTP_403_FORBIDDEN)
        
        # Open tickets waiting for a technician
        queryset = Ticket.objects.filter(status='open').select_related('user', 'assigned_technician')
        
        # Apply filters
        category = request.query_params.get('category')
        sub_category = request.query_params.get('sub_category')
        priority = request.query_params.get('priority')
        address = request.query_params.get('address')
        min_budget = request.query_params.get('min_budget')
        max_budget = request.query_params.get('max_budget')

        if category and category.lower() != 'all':
            queryset = queryset.filter(category_id=category)
        if sub_category and sub_category.lower() != 'all':
            queryset = queryset.filter(sub_category_id=sub_category)
        if priority and priority.lower() != 'all':
            queryset = queryset.filter(priority=priority.lower())
        if address:
            queryset = queryset.filter(address__icontains=address)
        if min_budget:
            try:
                queryset = queryset.filter(budget__gte=float(min_budget))
            except ValueError:
                pass
        if max_budget:
            try:
                queryset = queryset.filter(budget__lte=float(max_budget))
            except ValueError:
                pass

        tickets = queryset.order_by('-created_at')
        
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(tickets, request)
        if page is not None:
            serializer = TicketSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = TicketSerializer(tickets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PublicJobsView(APIView):
    permission_classes = [] # Allow unauthenticated access

    def get(self, request):
        queryset = Ticket.objects.filter(status='open').select_related('user', 'assigned_technician')
        
        # Apply filters
        category = request.query_params.get('category')
        sub_category = request.query_params.get('sub_category')
        priority = request.query_params.get('priority')
        address = request.query_params.get('address')
        min_budget = request.query_params.get('min_budget')
        max_budget = request.query_params.get('max_budget')

        if category and category.lower() != 'all':
            queryset = queryset.filter(category_id=category)
        if sub_category and sub_category.lower() != 'all':
            queryset = queryset.filter(sub_category_id=sub_category)
        if priority and priority.lower() != 'all':
            queryset = queryset.filter(priority=priority.lower())
        if address:
            queryset = queryset.filter(address__icontains=address)
        if min_budget:
            try:
                queryset = queryset.filter(budget__gte=float(min_budget))
            except ValueError:
                pass
        if max_budget:
            try:
                queryset = queryset.filter(budget__lte=float(max_budget))
            except ValueError:
                pass

        tickets = queryset.order_by('-created_at')
        
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(tickets, request)
        if page is not None:
            serializer = TicketSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = TicketSerializer(tickets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PublicJobDetailView(APIView):
    permission_classes = [] # Allow unauthenticated access

    def get(self, request, pk):
        try:
            ticket = Ticket.objects.get(pk=pk, status='open')
            serializer = TicketSerializer(ticket)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Ticket.DoesNotExist:
            return Response({"error": "Job not found or no longer available."}, status=status.HTTP_404_NOT_FOUND)

class AcceptTicketView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if request.user.role != 'technician':
            return Response({"error": "Only technicians can accept tickets."}, status=status.HTTP_403_FORBIDDEN)
            
        # Check if technician is approved by admin
        try:
            if not request.user.technician_profile.availability_status:
                return Response({"error": "Your account is pending admin approval. You cannot accept jobs yet."}, status=status.HTTP_403_FORBIDDEN)
        except Exception:
            return Response({"error": "Technician profile not found."}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            ticket = Ticket.objects.get(pk=pk, status='open')
        except Ticket.DoesNotExist:
            return Response({"error": "Ticket not found or already assigned."}, status=status.HTTP_404_NOT_FOUND)
        
        # Accept the ticket
        ticket.status = 'assigned'
        ticket.assigned_technician = request.user
        ticket.save()

        # Send Notification to Customer
        from authsystem.utils import create_and_send_notification
        create_and_send_notification(
            user=ticket.user,
            message=f"Your Ticket #{ticket.id} has been assigned to {request.user.name}",
            link=f"/dashboard/customer/ticket/{ticket.id}"
        )

        serializer = TicketSerializer(ticket)
        return Response({
            "message": "Ticket successfully accepted.",
            "ticket": serializer.data
        }, status=status.HTTP_200_OK)

class TechnicianDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'technician':
            return Response({"error": "Only technicians can access the dashboard."}, status=status.HTTP_403_FORBIDDEN)
        
        # Return only tickets assigned to this technician
        tickets = Ticket.objects.filter(assigned_technician=request.user).select_related('user', 'assigned_technician').order_by('-updated_at')
        
        paginator = PageNumberPagination()
        page = paginator.paginate_queryset(tickets, request)
        if page is not None:
            serializer = TicketSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = TicketSerializer(tickets, many=True)
        return Response({
            "assigned_tickets": serializer.data
        }, status=status.HTTP_200_OK)

class TicketCompleteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if request.user.role != 'technician':
            return Response({"error": "Only technicians can complete tickets."}, status=status.HTTP_403_FORBIDDEN)
            
        try:
            ticket = Ticket.objects.get(pk=pk, assigned_technician=request.user)
        except Ticket.DoesNotExist:
            return Response({"error": "Ticket not found or not assigned to you."}, status=status.HTTP_404_NOT_FOUND)
            
        # Optional: ensure status is 'assigned' or 'in_progress'
        if ticket.status in ['done', 'pending_confirmation']:
            return Response({"error": "Ticket is already completed or pending confirmation."}, status=status.HTTP_400_BAD_REQUEST)
            
        ticket.status = 'pending_confirmation'
        ticket.save()
        
        # Send Notification to Customer
        from authsystem.utils import create_and_send_notification
        create_and_send_notification(
            user=ticket.user,
            message=f"Job complete! Ticket #{ticket.id} is pending your payment.",
            link=f"/dashboard/customer/payments"
        )
        
        serializer = TicketSerializer(ticket)
        return Response({
            "message": "Ticket marked as complete. Pending customer confirmation.",
            "ticket": serializer.data
        }, status=status.HTTP_200_OK)
