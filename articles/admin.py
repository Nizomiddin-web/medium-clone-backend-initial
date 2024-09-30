from django.contrib import admin

# Register your models here.
from articles.models import Topic, Article


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description', 'is_active']
    list_display_links = ['name']
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'title', 'summary', 'content']
