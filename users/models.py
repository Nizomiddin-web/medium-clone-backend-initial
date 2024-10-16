from django.apps import apps
from django.conf import settings
from django.contrib.postgres.indexes import HashIndex
from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser
import os
from django_resized import ResizedImageField
import uuid

from articles.models import Article, Topic
from users.errors import BIRTH_YEAR_ERROR_MSG


def file_upload(instance, filename):
    """This function is used to upload the user's avatar"""
    ext = filename.split('.')[-1]
    filename = f"{instance.username}.{ext}"
    return os.path.join('users/avatars', filename)


# Create your models here.

class CustomUser(AbstractUser):
    """This model represent a custom user"""
    middle_name = models.CharField(max_length=30, blank=True, null=True)
    avatar = ResizedImageField(size=[300, 300], crop=['top', 'left'], upload_to=file_upload, blank=True)
    birth_year = models.IntegerField(
        validators=[
            validators.MinValueValidator(settings.BIRTH_YEAR_MIN),
            validators.MaxValueValidator(settings.BIRTH_YEAR_MAX)
        ],
        null=True,
        blank=True
    )

    def clean(self):
        super().clean()
        if self.birth_year and not (settings.BIRTH_YEAR_MIN < self.birth_year < settings.BIRTH_YEAR_MAX):
            raise ValidationError(BIRTH_YEAR_ERROR_MSG)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        db_table = "user"
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-date_joined"]  # describing order joined

        indexes = [
            HashIndex(fields=['first_name'], name='%(class)s_first_name_hash_idx'),
            HashIndex(fields=['last_name'], name='%(class)s_last_name_hash_idx'),
            HashIndex(fields=['middle_name'], name='%(class)s_middle_name_hash_idx'),
            models.Index(fields=['username'], name='%(class)s_username_idx'),
        ]

        constraints = [
            models.CheckConstraint(
                check=models.Q(birth_year__gt=settings.BIRTH_YEAR_MIN) & models.Q(
                    birth_year__lt=settings.BIRTH_YEAR_MAX),
                name='check_birth_year_range'
            )
        ]

    def __str__(self):
        """This method returns the full name of the user"""
        if self.full_name:
            return self.full_name
        else:
            return self.email or self.username

    @property
    def full_name(self):
        """This function return user's full name."""
        return f"{self.last_name} {self.first_name} {self.middle_name}"


class Recommendation(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='recommendations')
    more_recommend = models.ManyToManyField(Topic, related_name='more_recommended_by_users', blank=True)
    less_recommend = models.ManyToManyField(Topic, related_name='less_recommended_by_users', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'recommendation'
        verbose_name = 'Recommendation'
        verbose_name_plural = 'Recommendations'
        ordering = ['-created_at']

    def add_to_more_recommend(self, article):
        article_topics = article.topics.all()
        self.less_recommend.remove(*article_topics)  # `less_recommend` dan olib tashlang
        self.more_recommend.add(*article_topics)  # `more_recommend` ga qo'shish
        article.is_recommend = True
        article.save()

    def add_to_less_recommend(self, article):
        article_topics = article.topics.all()
        article.is_recommend = False
        article.save()
        # `more_recommend` ichida yo'qligini tekshirish
        if not article_topics.filter(id__in=self.more_recommend.all()).exists():
            self.less_recommend.add(*article_topics)  # Faqat `more_recommend` da yo'q bo'lsa qo'shish

    def __str__(self):
        return f"Recommendations for {self.user.username}"


class ReadingHistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='reading_history')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'reading_history'
        verbose_name = 'Reading history'
        verbose_name_plural = 'Reading Histories'

    def __str__(self):
        return f"{self.user} history  {self.article}"

class Follow(models.Model):
    follower = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name="follow_authors")
    followee = models.ForeignKey(CustomUser,on_delete=models.CASCADE,related_name="followers")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table='follow'
        verbose_name='Follow'
        verbose_name_plural='Follows'

    def __str__(self):
        return f"{self.follower} follow to {self.followee}"

