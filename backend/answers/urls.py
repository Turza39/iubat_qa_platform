from django.urls import path
from .views import AnswerListView

urlpatterns = [
    path('questions/<int:question_id>/', AnswerListView.as_view(), name='answer_list'),
]