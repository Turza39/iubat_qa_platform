from rest_framework import serializers
from .models import Question, Tag
from users.serializers import UserPublicSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Tag
        fields = ['id', 'name', 'slug']


class QuestionListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for question lists (home page, profile page).
    """
    author       = UserPublicSerializer(read_only=True)
    tags         = TagSerializer(many=True, read_only=True)
    upvote_count = serializers.IntegerField(read_only=True)
    answer_count = serializers.IntegerField(read_only=True)

    class Meta:
        model  = Question
        fields = [
            'id', 'title', 'author', 'tags',
            'upvote_count', 'answer_count', 'created_at'
        ]


class QuestionDetailSerializer(serializers.ModelSerializer):
    """
    Full serializer for the question detail page.
    """
    author       = UserPublicSerializer(read_only=True)
    tags         = TagSerializer(many=True, read_only=True)
    tag_ids      = serializers.PrimaryKeyRelatedField(
                       queryset=Tag.objects.all(),
                       many=True,
                       write_only=True,
                       required=False,
                       source='tags'
                   )
    upvote_count = serializers.IntegerField(read_only=True)
    answer_count = serializers.IntegerField(read_only=True)

    class Meta:
        model  = Question
        fields = [
            'id', 'title', 'body', 'author', 'tags', 'tag_ids',
            'upvote_count', 'answer_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']

    def validate_tag_ids(self, value):
        if len(value) > 5:
            raise serializers.ValidationError('You can add a maximum of 5 tags.')
        return value

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        question = Question.objects.create(**validated_data)
        question.tags.set(tags)
        return question

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tags is not None:
            instance.tags.set(tags)
        return instance