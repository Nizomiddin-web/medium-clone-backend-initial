from django_filters import rest_framework as filters

from articles.models import Article


class ArticleFilter(filters.FilterSet):
    get_top_articles = filters.NumberFilter(field_name="views_count", method="filter_top_articles")
    topic_id = filters.NumberFilter(field_name="topics", method="filter_topic_id")

    class Meta:
        model = Article
        fields = ['get_top_articles', 'topic_id', 'is_recommend']

    def filter_top_articles(self, queryset, name, value):
        if value:
            return queryset.order_by('-views_count')[:value]
        return queryset

    def filter_topic_id(self, queryset, name, value):
        if value:
            return queryset.filter(topics__id=value)
        return queryset
