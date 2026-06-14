from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import User, TechnicianProfile, OTP

@admin.register(User)
class UserAdmin(ModelAdmin):
    list_display = ('email', 'name', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('email', 'name')

@admin.register(TechnicianProfile)
class TechnicianProfileAdmin(ModelAdmin):
    list_display = ('user', 'experience_years', 'availability_status', 'rating')
    list_filter = ('availability_status',)
    search_fields = ('user__email', 'user__name', 'skills')

@admin.register(OTP)
class OTPAdmin(ModelAdmin):
    list_display = ('user', 'otp_code', 'created_at', 'is_verified')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('user__email',)
