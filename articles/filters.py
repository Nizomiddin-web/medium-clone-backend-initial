from django.db.models import Q
from django_filters import rest_framework as filters

from articles.models import Article


class ArticleFilter(filters.FilterSet):
    search = filters.CharFilter(field_name="title", method="search_filter_method")
    get_top_articles = filters.NumberFilter(field_name="views_count", method="filter_top_articles")
    topic_id = filters.NumberFilter(field_name="topics", method="filter_topic_id")
    is_user_favorites = filters.BooleanFilter(method='filter_favorites')
    is_reading_history = filters.BooleanFilter(method='filter_reading_history')
    is_author_article = filters.BooleanFilter(method='filter_author_article')

    class Meta:
        model = Article
        fields = ['get_top_articles', 'topic_id', 'is_recommend', 'search', 'is_user_favorites', 'is_reading_history','is_author_article']

    def filter_top_articles(self, queryset, name, value):
        if value:
            return queryset.order_by('-views_count')[:value]
        return queryset

    def filter_topic_id(self, queryset, name, value):
        if value:
            return queryset.filter(topics__id=value)
        return queryset

    def search_filter_method(self, queryset, name, value):
        if value:
            # Create a Q object to combine all the search criteria
            query = Q(title__icontains=value) | Q(topics__name__icontains=value) | Q(summary__icontains=value) | Q(
                content__icontains=value)
            # Use the Q object to filter the queryset
            return queryset.filter(query)

        return queryset

    def filter_favorites(self, queryset, name, value):
        if value:
            user = self.request.user
            return queryset.filter(favorite_article__user=user)
        return queryset

    def filter_reading_history(self, queryset, name, value):
        if value:
            user = self.request.user
            return queryset.filter(reading_history__user=user)
        return queryset

    def filter_author_article(self,queryset,name,value):
        if value:
            user = self.request.user
            return queryset.filter(author=user)
        return queryset