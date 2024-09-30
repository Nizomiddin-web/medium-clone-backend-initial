import os

from django.db import models

# Create your models here.
from users.models import CustomUser


def upload_image(instance, filename):
    return os.path.join('articles/thumbnails', filename)


class StatusChoice(models.TextChoices):
    PENDING = 'pending', 'Pending'
    PUBLISHED = 'published', 'Published'


class Topic(models.Model):
    name = models.CharField()
    description = models.CharField()
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f"Topic: {self.name}"


class Article(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    summary = models.CharField(max_length=400)
    content = models.TextField()
    status = models.CharField(max_length=20, choices=StatusChoice.choices, default=StatusChoice.PENDING)
    thumbnail = models.ImageField(upload_to=upload_image)
    views_count = models.PositiveIntegerField(default=0)
    reads_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    topics = models.ManyToManyField(Topic)

    class Meta:
        db_table = 'article'
        verbose_name = 'Article'

class Clap(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='claps')
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='claps')
