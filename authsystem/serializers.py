from rest_framework import serializers
from .models import User, TechnicianProfile, OTP, Notification
from django.contrib.auth import authenticate

class TechnicianProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechnicianProfile
        fields = ['skills', 'experience_years', 'availability_status', 'rating']

class UserSerializer(serializers.ModelSerializer):
    technician_profile = TechnicianProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'role', 'phone', 'location', 'nid_number', 'created_at', 'is_active', 'technician_profile']

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    skills = serializers.CharField(source='technician_profile.skills', required=False, allow_blank=True)
    experience_years = serializers.IntegerField(source='technician_profile.experience_years', required=False)

    class Meta:
        model = User
        fields = ['name', 'phone', 'location', 'nid_number', 'skills', 'experience_years']
        read_only_fields = ['nid_number']

    def update(self, instance, validated_data):
        technician_data = validated_data.pop('technician_profile', {})
        
        instance.name = validated_data.get('name', instance.name)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.location = validated_data.get('location', instance.location)
        instance.save()

        if instance.role == 'technician' and technician_data:
            profile = instance.technician_profile
            profile.skills = technician_data.get('skills', profile.skills)
            profile.experience_years = technician_data.get('experience_years', profile.experience_years)
            profile.save()

        return instance

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'message', 'link', 'is_read', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['name', 'email', 'password', 'role', 'phone', 'location', 'nid_number']

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password'],
            role=validated_data.get('role', 'customer'),
            phone=validated_data.get('phone', ''),
            location=validated_data.get('location', ''),
            nid_number=validated_data.get('nid_number', '')
        )
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            if not user:
                raise serializers.ValidationError("Unable to log in with provided credentials.")
        else:
            raise serializers.ValidationError("Must include 'email' and 'password'.")

        data['user'] = user
        return data

class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6)
