from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Count, Q
from tickets.models import Ticket
from authsystem.models import User
from payment.models import Payment

class CustomerAnalyzeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'customer':
            return Response({"error": "Only customers can view this dashboard."}, status=403)
            
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = now - timedelta(days=7)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # Base queryset for customer
        tickets = Ticket.objects.filter(user=request.user)

        # Posts stats
        total_posts = tickets.count()
        today_posts = tickets.filter(created_at__gte=today_start).count()
        seven_days_posts = tickets.filter(created_at__gte=week_start).count()
        month_posts = tickets.filter(created_at__gte=month_start).count()

        # Work done and accepted stats
        # Accepted means a technician has it or it's done. 
        total_accepted = tickets.filter(status__in=['assigned', 'in_progress', 'pending_confirmation', 'done']).count()
        total_work_done = tickets.filter(status='done').count()

        # Payment stats
        # Total money spent on tickets by this customer where payment is completed
        total_payments = Payment.objects.filter(ticket__user=request.user, status='completed').aggregate(Sum('amount'))['amount__sum'] or 0.00

        return Response({
            "total_posts": total_posts,
            "today_posts": today_posts,
            "seven_days_posts": seven_days_posts,
            "this_month_posts": month_posts,
            "total_accepted": total_accepted,
            "total_work_done": total_work_done,
            "total_payments_spent": float(total_payments)
        })

class TechnicianAnalyzeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'technician':
            return Response({"error": "Only technicians can view this dashboard."}, status=403)

        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = now - timedelta(days=7)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

        # Base queryset for technician
        tickets = Ticket.objects.filter(assigned_technician=request.user)

        total_accepted = tickets.count()
        
        done_tickets = tickets.filter(status='done')
        total_work_done = done_tickets.count()
        today_work_done = done_tickets.filter(updated_at__gte=today_start).count()
        seven_days_work_done = done_tickets.filter(updated_at__gte=week_start).count()
        month_work_done = done_tickets.filter(updated_at__gte=month_start).count()
        year_work_done = done_tickets.filter(updated_at__gte=year_start).count()

        # Financials
        total_money_received = Payment.objects.filter(ticket__assigned_technician=request.user, status='completed').aggregate(Sum('amount'))['amount__sum'] or 0.00

        return Response({
            "total_accepted": total_accepted,
            "total_work_done": total_work_done,
            "today_work_done": today_work_done,
            "seven_days_work_done": seven_days_work_done,
            "this_month_work_done": month_work_done,
            "this_year_work_done": year_work_done,
            "total_money_received": float(total_money_received)
        })

class AdminAnalyzeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # We allow any authenticated user to view this per the user's request.
        # In production, you might enforce: if not request.user.is_staff: return Response(status=403)
        
        total_users = User.objects.count()
        total_customers = User.objects.filter(role='customer').count()
        total_technicians = User.objects.filter(role='technician').count()

        total_tickets = Ticket.objects.count()
        completed_tickets = Ticket.objects.filter(status='done').count()

        total_transfer_money = Payment.objects.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0.00

        return Response({
            "total_users": total_users,
            "total_customers": total_customers,
            "total_technicians": total_technicians,
            "total_tickets_created": total_tickets,
            "total_tickets_completed": completed_tickets,
            "total_transfer_money": float(total_transfer_money)
        })
