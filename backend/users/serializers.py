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
    class Meta:
        model  = User
        fields = ['id', 'username', 'verification_status']


class UserProfileSerializer(serializers.ModelSerializer):
    # Write-only field, not stored directly
    current_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model  = User
        fields = [
            'id', 'username', 'email',
            'verification_status', 'date_joined',
            'current_password',               # ← added
        ]
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

    def validate(self, data):
        user = self.context['request'].user

        # If username or email is being changed, require current password
        username_changed = 'username' in data and data['username'] != user.username
        email_changed    = 'email'    in data and data['email']    != user.email

        if username_changed or email_changed:
            current_password = data.get('current_password', '')
            if not current_password:
                raise serializers.ValidationError({
                    'current_password': 'Please enter your current password to save changes.'
                })
            if not user.check_password(current_password):
                raise serializers.ValidationError({
                    'current_password': 'Incorrect password. Please try again.'
                })

        return data

    def update(self, instance, validated_data):
        # Remove current_password before saving, it's not a model field
        validated_data.pop('current_password', None)
        return super().update(instance, validated_data)


class VerificationRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model  = VerificationRequest
        fields = ['id', 'id_card_image', 'status', 'submitted_at']
        read_only_fields = ['id', 'status', 'submitted_at']

    def validate_id_card_image(self, value):
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError('Image size must not exceed 5MB.')
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png']
        if value.content_type not in allowed_types:
            raise serializers.ValidationError('Only JPG, JPEG and PNG files are allowed.')
        return value