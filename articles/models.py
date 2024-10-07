import os

from django.conf import settings
from django.db import models
# Create your models here.



def upload_image(instance, filename):
    return os.path.join('articles/thumbnails', filename)


class StatusChoice(models.TextChoices):
    PENDING = 'pending', 'Pending'
    PUBLISHED = 'publish', 'Publish'


class Topic(models.Model):
    name = models.CharField()
    description = models.CharField()
    is_active = models.BooleanField(default=False)

    class Meta:
        db_table = 'topic'
        verbose_name = 'Topic'
        verbose_name_plural = 'Topics'
        ordering = ['name']

    def __str__(self):
        return f"Topic: {self.name}"


class Article(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    summary = models.CharField(max_length=400)
    content = models.TextField()
    status = models.CharField(max_length=20, choices=StatusChoice.choices, default=StatusChoice.PENDING)
    thumbnail = models.ImageField(upload_to=upload_image, null=True, blank=True)
    views_count = models.PositiveIntegerField(default=0)
    reads_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    topics = models.ManyToManyField(Topic)
    is_recommend = models.BooleanField(default=False)

    class Meta:
        db_table = 'article'
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
        ordering = ['-created_at']

    def __str__(self):
        return f"Article ID: {self.id}"


class Clap(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='claps')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='claps')


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'comment'
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.user.username}"
