"""
Views for user authentication
"""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import secrets

from .models import EmailVerificationToken, PasswordResetToken
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserRegistrationSerializer,
    UserSerializer,
    PasswordChangeSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    SimplePasswordResetSerializer,
)

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom token view that returns user data along with tokens"""
    serializer_class = CustomTokenObtainPairSerializer


class UserRegistrationView(generics.CreateAPIView):
    """View for user registration"""
    
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        """Create a new user and send verification email"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Create email verification token
        token = secrets.token_urlsafe(32)
        EmailVerificationToken.objects.create(
            user=user,
            token=token,
            expires_at=timezone.now() + timedelta(hours=24)
        )
        
        # TODO: Send verification email via Celery task
        # from apps.notifications.tasks import send_verification_email
        # send_verification_email.delay(user.id, token)
        
        return Response({
            'user': UserSerializer(user).data,
            'message': 'Registration successful. Please check your email to verify your account.'
        }, status=status.HTTP_201_CREATED)


class EmailVerificationView(APIView):
    """View for email verification"""
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Verify email with token"""
        token = request.data.get('token')
        
        if not token:
            return Response(
                {'error': 'Token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            verification = EmailVerificationToken.objects.get(token=token)
            
            if not verification.is_valid():
                return Response(
                    {'error': 'Token is invalid or expired'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user = verification.user
            user.is_email_verified = True
            user.save()
            
            verification.is_used = True
            verification.save()
            
            return Response({
                'message': 'Email verified successfully'
            }, status=status.HTTP_200_OK)
            
        except EmailVerificationToken.DoesNotExist:
            return Response(
                {'error': 'Invalid token'},
                status=status.HTTP_400_BAD_REQUEST
            )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """View for retrieving and updating user profile"""
    
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """Return the current user"""
        return self.request.user


class PasswordChangeView(APIView):
    """View for changing password"""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Change user password"""
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            return Response({
                'message': 'Password changed successfully'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    """View for requesting password reset"""
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Request password reset"""
        serializer = PasswordResetRequestSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            try:
                user = User.objects.get(email=email)
                
                # Create password reset token
                token = secrets.token_urlsafe(32)
                PasswordResetToken.objects.create(
                    user=user,
                    token=token,
                    expires_at=timezone.now() + timedelta(hours=1)
                )
                
                # TODO: Send password reset email via Celery task
                # from apps.notifications.tasks import send_password_reset_email
                # send_password_reset_email.delay(user.id, token)
                
            except User.DoesNotExist:
                # Don't reveal if email exists or not
                pass
            
            return Response({
                'message': 'If the email exists, a password reset link has been sent.'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    """View for confirming password reset"""
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Confirm password reset with token"""
        serializer = PasswordResetConfirmSerializer(data=request.data)
        
        if serializer.is_valid():
            token = serializer.validated_data['token']
            
            try:
                reset_token = PasswordResetToken.objects.get(token=token)
                
                if not reset_token.is_valid():
                    return Response(
                        {'error': 'Token is invalid or expired'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                user = reset_token.user
                user.set_password(serializer.validated_data['password'])
                user.save()
                
                reset_token.is_used = True
                reset_token.save()
                
                return Response({
                    'message': 'Password reset successfully'
                }, status=status.HTTP_200_OK)
                
            except PasswordResetToken.DoesNotExist:
                return Response(
                    {'error': 'Invalid token'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SimplePasswordResetCheckView(APIView):
    """View to check if email or phone exists for password reset"""
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Check if email or phone exists"""
        email = request.data.get('email')
        phone_number = request.data.get('phone_number')
        
        if not email and not phone_number:
            return Response(
                {'error': 'Email or phone number is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = None
        if email:
            user = User.objects.filter(email=email).first()
        elif phone_number:
            user = User.objects.filter(phone_number=phone_number).first()
        
        if user:
            return Response({
                'exists': True,
                'user_id': user.id,
                'email': user.email,
                'message': 'Account found. You can now reset your password.'
            }, status=status.HTTP_200_OK)
        
        return Response({
            'exists': False,
            'message': 'No account found with that email or phone number.'
        }, status=status.HTTP_404_NOT_FOUND)


class SimplePasswordResetView(APIView):
    """View to reset password directly after verification"""
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        """Reset password directly"""
        serializer = SimplePasswordResetSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            phone_number = serializer.validated_data.get('phone_number')
            new_password = serializer.validated_data['new_password']
            
            user = None
            if email:
                user = User.objects.filter(email=email).first()
            elif phone_number:
                user = User.objects.filter(phone_number=phone_number).first()
            
            if not user:
                return Response(
                    {'error': 'No account found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            user.set_password(new_password)
            user.save()
            
            return Response({
                'message': 'Password reset successfully. You can now login with your new password.'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
