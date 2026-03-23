from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import (
    RegisterSerializer,
    UserProfileSerializer,
    VerificationRequestSerializer,
)
from .models import VerificationRequest

User = get_user_model()


class RegisterView(APIView):
    """
    POST /api/users/register/
    Register a new user account.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {
                    'message'  : 'Account created successfully.',
                    'user_id'  : user.id,
                    'username' : user.username,
                    'email'    : user.email,
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    """
    GET  /api/users/profile/   - retrieve logged-in user's profile and their questions
    PUT  /api/users/profile/   - update logged-in user's username or email
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user, context={'request': request})

        # Import here to avoid circular imports
        from questions.serializers import QuestionListSerializer
        user_questions = request.user.questions.all()
        questions_serializer = QuestionListSerializer(
            user_questions,
            many=True,
            context={'request': request}
        )

        return Response({
            'profile'   : serializer.data,
            'questions' : questions_serializer.data,
        })

    def put(self, request):
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Profile updated successfully.',
                'profile': serializer.data,
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerificationRequestView(APIView):
    """
    GET  /api/users/verify/  - check current verification status
    POST /api/users/verify/  - submit ID card image for verification
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            verification = VerificationRequest.objects.get(user=request.user)
            serializer   = VerificationRequestSerializer(verification)
            return Response(serializer.data)
        except VerificationRequest.DoesNotExist:
            return Response({
                'status'  : 'not_submitted',
                'message' : 'You have not submitted a verification request yet.',
            })

    def post(self, request):
        user = request.user

        # Block if already verified
        if user.verification_status == 'verified':
            return Response(
                {'message': 'You are already verified.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Block if pending
        if user.verification_status == 'pending':
            return Response(
                {'message': 'Your verification request is already under review.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = VerificationRequestSerializer(data=request.data)
        if serializer.is_valid():
            # If a rejected request exists, update it instead of creating a new one
            verification, created = VerificationRequest.objects.update_or_create(
                user     = user,
                defaults = {
                    'id_card_image' : serializer.validated_data['id_card_image'],
                    'status'        : 'pending',
                }
            )
            # Update user's verification status to pending
            user.verification_status = 'pending'
            user.save()

            return Response(
                {
                    'message'      : 'Verification request submitted successfully.',
                    'submitted_at' : verification.submitted_at,
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)