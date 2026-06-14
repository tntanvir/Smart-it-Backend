from django.urls import path
from .views import CustomerAnalyzeView, TechnicianAnalyzeView, AdminAnalyzeView

urlpatterns = [
    path('customer/', CustomerAnalyzeView.as_view(), name='analyze-customer'),
    path('technician/', TechnicianAnalyzeView.as_view(), name='analyze-technician'),
    path('admin/', AdminAnalyzeView.as_view(), name='analyze-admin'),
]
