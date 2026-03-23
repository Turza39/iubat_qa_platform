from django.urls import path
from .views import QuestionListView, QuestionDetailView, TagListView

urlpatterns = [
    path('',         QuestionListView.as_view(),   name='question_list'),
    path('<int:pk>/', QuestionDetailView.as_view(), name='question_detail'),
    path('tags/',    TagListView.as_view(),         name='tag_list'),
]