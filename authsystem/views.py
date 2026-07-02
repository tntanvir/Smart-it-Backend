from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import User, OTP, TechnicianProfile, Notification
from .serializers import RegisterSerializer, LoginSerializer, OTPVerifySerializer, UserSerializer, UserProfileUpdateSerializer, NotificationSerializer

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            if user.role == 'technician':
                TechnicianProfile.objects.create(user=user)

            # Generate OTP
            otp = OTP.objects.create(user=user)
            otp.generate_otp()

            # Send Email
            subject = 'Verify your account - TechBridge Support'
            text_content = f'Hello {user.name},\nYour OTP code is {otp.otp_code}. It is valid for 10 minutes.'
            html_content = render_to_string('authsystem/otp_email.html', {'name': user.name, 'otp_code': otp.otp_code})
            
            msg = EmailMultiAlternatives(
                subject,
                text_content,
                'noreply@smartitsupport.com',
                [user.email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send(fail_silently=False)

            return Response({
                "message": "User registered successfully. Please check your email for the OTP.",
                "email": user.email
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp_code = serializer.validated_data['otp_code']

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

            try:
                otp = OTP.objects.filter(user=user, otp_code=otp_code, is_verified=False).latest('created_at')
            except OTP.DoesNotExist:
                return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)

            if otp.is_valid():
                otp.is_verified = True
                otp.save()

                user.is_active = True
                user.save()

                # Notify admin if user is a technician
                if user.role == 'technician':
                    from django.conf import settings
                    try:
                        subject = f'Action Required: New Technician Registration ({user.name})'
                        text_content = f'A new technician ({user.name}, Email: {user.email}) has just completed registration and OTP verification.\n\nPlease log in to the Django admin dashboard, check their TechnicianProfile, and approve them by checking the "availability_status" box so they can start accepting jobs.'
                        admin_msg = EmailMultiAlternatives(
                            subject,
                            text_content,
                            settings.EMAIL_HOST_USER,
                            [settings.EMAIL_HOST_USER]
                        )
                        admin_msg.send(fail_silently=False)
                    except Exception as e:
                        print("Failed to send admin notification email:", str(e))

                refresh = RefreshToken.for_user(user)

                return Response({
                    "message": "Email verified successfully.",
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                    "user": UserSerializer(user).data
                }, status=status.HTTP_200_OK)
            else:
                return Response({"error": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            if not user.is_active:
                return Response({"error": "Account is not active. Please verify your email."}, status=status.HTTP_403_FORBIDDEN)
            
            refresh = RefreshToken.for_user(user)
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "user": UserSerializer(user).data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        serializer = UserProfileUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            updated_serializer = UserSerializer(request.user)
            return Response(updated_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(user=request.user)
        # Optional: Add simple pagination or limit
        notifications = notifications[:50]
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class NotificationReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            notification = Notification.objects.get(id=pk, user=request.user)
            notification.is_read = True
            notification.save()
            return Response({"success": "Notification marked as read"}, status=status.HTTP_200_OK)
        except Notification.DoesNotExist:
            return Response({"error": "Notification not found"}, status=status.HTTP_404_NOT_FOUND)
