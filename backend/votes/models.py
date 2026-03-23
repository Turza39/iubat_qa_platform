from django.db import models
from django.conf import settings
from questions.models import Question
from answers.models import Answer


class Vote(models.Model):
    user       = models.ForeignKey(
                     settings.AUTH_USER_MODEL,
                     on_delete=models.CASCADE,
                     related_name='votes'
                 )
    question   = models.ForeignKey(
                     Question,
                     on_delete=models.CASCADE,
                     related_name='votes',
                     null=True,
                     blank=True
                 )
    answer     = models.ForeignKey(
                     Answer,
                     on_delete=models.CASCADE,
                     related_name='votes',
                     null=True,
                     blank=True
                 )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'votes'
        # Prevents a user from voting twice on the same question or answer
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'question'],
                condition=models.Q(question__isnull=False),
                name='unique_vote_per_user_per_question'
            ),
            models.UniqueConstraint(
                fields=['user', 'answer'],
                condition=models.Q(answer__isnull=False),
                name='unique_vote_per_user_per_answer'
            ),
        ]

    def __str__(self):
        if self.question:
            return f'{self.user.username} voted on question: {self.question.title}'
        return f'{self.user.username} voted on answer by: {self.answer.author.username}'