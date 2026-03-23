from django.urls import path
from .views import QuestionVoteView, AnswerVoteView

urlpatterns = [
    path('questions/<int:question_id>/', QuestionVoteView.as_view(), name='question_vote'),
    path('answers/<int:answer_id>/',     AnswerVoteView.as_view(),   name='answer_vote'),
]