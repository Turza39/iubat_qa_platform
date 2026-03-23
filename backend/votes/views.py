from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from questions.models import Question
from answers.models import Answer
from .models import Vote


class QuestionVoteView(APIView):
    """
    POST /api/votes/questions/<question_id>/   - toggle upvote on a question
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, question_id):
        try:
            question = Question.objects.get(pk=question_id)
        except Question.DoesNotExist:
            return Response(
                {'message': 'Question not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Cannot vote on your own question
        if question.author == request.user:
            return Response(
                {'message': 'You cannot vote on your own question.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Toggle vote
        vote = Vote.objects.filter(user=request.user, question=question).first()
        if vote:
            vote.delete()
            return Response({
                'message'      : 'Vote removed.',
                'upvote_count' : question.upvote_count,
            })
        else:
            Vote.objects.create(user=request.user, question=question)
            return Response({
                'message'      : 'Vote added.',
                'upvote_count' : question.upvote_count,
            })


class AnswerVoteView(APIView):
    """
    POST /api/votes/answers/<answer_id>/   - toggle upvote on an answer
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, answer_id):
        try:
            answer = Answer.objects.get(pk=answer_id)
        except Answer.DoesNotExist:
            return Response(
                {'message': 'Answer not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Cannot vote on your own answer
        if answer.author == request.user:
            return Response(
                {'message': 'You cannot vote on your own answer.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Toggle vote
        vote = Vote.objects.filter(user=request.user, answer=answer).first()
        if vote:
            vote.delete()
            return Response({
                'message'      : 'Vote removed.',
                'upvote_count' : answer.upvote_count,
            })
        else:
            Vote.objects.create(user=request.user, answer=answer)
            return Response({
                'message'      : 'Vote added.',
                'upvote_count' : answer.upvote_count,
            })