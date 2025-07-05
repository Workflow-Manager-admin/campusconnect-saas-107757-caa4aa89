from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
from .serializers import (
    UserSerializer, RegisterSerializer, CustomTokenObtainPairSerializer,
    ChangePasswordSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer
)
from .models import User

class RegisterView(generics.CreateAPIView):
    """
    PUBLIC_INTERFACE
    API endpoint for user registration.
    """
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    PUBLIC_INTERFACE
    Custom token obtain view with additional user information.
    """
    serializer_class = CustomTokenObtainPairSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    PUBLIC_INTERFACE
    API endpoint for retrieving and updating user profile.
    """
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user

class ChangePasswordView(generics.UpdateAPIView):
    """
    PUBLIC_INTERFACE
    API endpoint for changing password.
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({'message': 'Password updated successfully'}, status=status.HTTP_200_OK)

class PasswordResetRequestView(generics.CreateAPIView):
    """
    PUBLIC_INTERFACE
    API endpoint for requesting password reset.
    """
    serializer_class = PasswordResetRequestSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            
            # Send password reset email
            reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}&email={email}"
            send_mail(
                'Password Reset Request',
                f'Click the following link to reset your password: {reset_url}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            return Response(
                {'message': 'Password reset email has been sent'},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {'message': 'User with this email does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

class PasswordResetConfirmView(generics.CreateAPIView):
    """
    PUBLIC_INTERFACE
    API endpoint for confirming password reset.
    """
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token = serializer.validated_data['token']
        email = request.data.get('email')
        
        try:
            user = User.objects.get(email=email)
            if default_token_generator.check_token(user, token):
                user.set_password(serializer.validated_data['new_password'])
                user.save()
                return Response(
                    {'message': 'Password has been reset successfully'},
                    status=status.HTTP_200_OK
                )
            return Response(
                {'message': 'Invalid or expired token'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except User.DoesNotExist:
            return Response(
                {'message': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )
