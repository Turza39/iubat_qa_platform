from django.db import models
from django.conf import settings


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        db_table  = 'tags'
        ordering  = ['name']

    def __str__(self):
        return self.name


class Question(models.Model):
    title      = models.CharField(max_length=200)
    body       = models.TextField(max_length=5000)
    author     = models.ForeignKey(
                     settings.AUTH_USER_MODEL,
                     on_delete=models.CASCADE,
                     related_name='questions'
                 )
    tags       = models.ManyToManyField(
                     Tag,
                     blank=True,
                     related_name='questions'
                 )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'questions'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def upvote_count(self):
        return self.votes.count()

    @property
    def answer_count(self):
        return self.answers.count()