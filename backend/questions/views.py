from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from .models import Question, Tag
from .serializers import QuestionDetailSerializer, QuestionListSerializer, TagSerializer


class QuestionListView(APIView):
    """
    GET  /api/questions/         - list all questions (newest first), supports search
    POST /api/questions/         - create a new question (logged-in users only)
    """
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def get(self, request):
        questions = Question.objects.all()

        # Search by keyword in title or body
        search = request.query_params.get('search', None)
        if search:
            questions = questions.filter(
                Q(title__icontains=search) | Q(body__icontains=search)
            )

        # Filter by tag slug
        tag = request.query_params.get('tag', None)
        if tag:
            questions = questions.filter(tags__slug=tag)

        serializer = QuestionListSerializer(questions, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        serializer = QuestionDetailSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QuestionDetailView(APIView):
    """
    GET /api/questions/<id>/   - retrieve a single question with its answers
    """
    permission_classes = [permissions.AllowAny]

    def get_object(self, pk):
        try:
            return Question.objects.get(pk=pk)
        except Question.DoesNotExist:
            return None

    def get(self, request, pk):
        question = self.get_object(pk)
        if not question:
            return Response(
                {'message': 'Question not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Import here to avoid circular imports
        from answers.serializers import AnswerSerializer
        question_serializer = QuestionDetailSerializer(question, context={'request': request})
        answers             = question.answers.all().order_by('-created_at')
        answer_serializer   = AnswerSerializer(answers, many=True, context={'request': request})

        return Response({
            'question' : question_serializer.data,
            'answers'  : answer_serializer.data,
        })


class TagListView(APIView):
    """
    GET /api/questions/tags/   - list all available tags
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        tags       = Tag.objects.all()
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data)