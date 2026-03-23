from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from questions.models import Question
from .models import Answer
from .serializers import AnswerSerializer


class AnswerListView(APIView):
    """
    POST /api/answers/questions/<question_id>/   - post an answer (verified users only)
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, question_id):
        # Only verified students can post answers
        if not request.user.is_verified:
            return Response(
                {
                    'message': 'Only verified students can post answers.',
                    'verification_status': request.user.verification_status,
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # Check question exists
        try:
            question = Question.objects.get(pk=question_id)
        except Question.DoesNotExist:
            return Response(
                {'message': 'Question not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AnswerSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(author=request.user, question=question)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)