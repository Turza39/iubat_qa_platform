from rest_framework import serializers
from .models import Answer
from users.serializers import UserPublicSerializer


class AnswerSerializer(serializers.ModelSerializer):
    author       = UserPublicSerializer(read_only=True)
    upvote_count = serializers.IntegerField(read_only=True)

    class Meta:
        model  = Answer
        fields = [
            'id', 'body', 'question', 'author',
            'upvote_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'question', 'created_at', 'updated_at']