from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import VerificationRequest

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password         = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model  = User
        fields = ['id', 'username', 'email', 'password', 'confirm_password']

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('This email is already registered.')
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('This username is already taken.')
        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError({'confirm_password': 'Passwords do not match.'})
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(
            email    = validated_data['email'],
            username = validated_data['username'],
            password = validated_data['password'],
        )
        return user


class UserPublicSerializer(serializers.ModelSerializer):
    """
    Used when showing author info on questions and answers.
    Only exposes safe public fields.
    """
    class Meta:
        model  = User
        fields = ['id', 'username', 'verification_status']


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Used for viewing and updating the logged-in user's own profile.
    """
    class Meta:
        model  = User
        fields = ['id', 'username', 'email', 'verification_status', 'date_joined']
        read_only_fields = ['id', 'verification_status', 'date_joined']

    def validate_email(self, value):
        user = self.context['request'].user
        if User.objects.filter(email=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError('This email is already in use.')
        return value

    def validate_username(self, value):
        user = self.context['request'].user
        if User.objects.filter(username=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError('This username is already taken.')
        return value


class VerificationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model  = VerificationRequest
        fields = ['id', 'id_card_image', 'status', 'submitted_at']
        read_only_fields = ['id', 'status', 'submitted_at']

    def validate_id_card_image(self, value):
        # Check file size (max 5MB)
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError('Image size must not exceed 5MB.')
        # Check file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png']
        if value.content_type not in allowed_types:
            raise serializers.ValidationError('Only JPG, JPEG and PNG files are allowed.')
        return value