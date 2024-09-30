# Create your views here.
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from articles.models import Article
from articles.serializers import ArticleCreateSerializer, ArticleDetailSerializer


class ArticlesView(ModelViewSet):
    queryset = Article.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return ArticleCreateSerializer
        if self.action == 'retrieve':
            return ArticleDetailSerializer
        return super().get_serializer_class()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        instance.views_count += 1
        instance.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)
