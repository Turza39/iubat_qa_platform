from django.db import models
from django.conf import settings
from questions.models import Question


class Answer(models.Model):
    body       = models.TextField(max_length=5000)
    question   = models.ForeignKey(
                     Question,
                     on_delete=models.CASCADE,
                     related_name='answers'
                 )
    author     = models.ForeignKey(
                     settings.AUTH_USER_MODEL,
                     on_delete=models.CASCADE,
                     related_name='answers'
                 )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'answers'
        ordering = ['-created_at']

    def __str__(self):
        return f'Answer by {self.author.username} on {self.question.title}'

    @property
    def upvote_count(self):
        return self.votes.count()