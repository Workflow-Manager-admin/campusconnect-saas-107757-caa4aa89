from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User

class UserSerializer(serializers.ModelSerializer):
    """
    PUBLIC_INTERFACE
    Serializer for User model.
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'user_type', 
                 'phone', 'profile_photo', 'is_active', 'date_joined')
        read_only_fields = ('id', 'date_joined')

class RegisterSerializer(serializers.ModelSerializer):
    """
    PUBLIC_INTERFACE
    Serializer for user registration.
    """
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name', 
                 'user_type', 'phone')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    PUBLIC_INTERFACE
    Custom token serializer to include additional user information.
    """
    def validate(self, attrs):
        data = super().validate(attrs)
        data.update({
            'user_id': str(self.user.id),
            'username': self.user.username,
            'email': self.user.email,
            'user_type': self.user.user_type,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name
        })
        return data

class ChangePasswordSerializer(serializers.Serializer):
    """
    PUBLIC_INTERFACE
    Serializer for password change.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect")
        return value

class PasswordResetRequestSerializer(serializers.Serializer):
    """
    PUBLIC_INTERFACE
    Serializer for password reset request.
    """
    email = serializers.EmailField(required=True)

class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    PUBLIC_INTERFACE
    Serializer for password reset confirmation.
    """
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
