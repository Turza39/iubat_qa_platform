from rest_framework import serializers
from .models import Vote


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Vote
        fields = ['id', 'user', 'question', 'answer', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']