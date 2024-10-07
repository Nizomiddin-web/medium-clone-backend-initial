from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from articles.filters import ArticleFilter
from articles.models import Article
from articles.permissions import IsOwnerOrReadOnly
from articles.serializers import ArticleCreateSerializer, ArticleDetailSerializer, ArticleListSerializer


class ArticlesView(ModelViewSet):
    queryset = Article.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ArticleFilter
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        if self.action == 'list':
            return Article.objects.filter(status="publish").annotate(
                comments_count=Count('comments'),
                claps_count=Count('claps')
            )
        return super().get_queryset()

    def get_serializer_class(self):
        if self.action == 'create':
            return ArticleCreateSerializer
        if self.action == 'retrieve':
            return ArticleDetailSerializer
        if self.action == 'list':
            return ArticleListSerializer
        return super().get_serializer_class()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status == "pending":
            return Response({"detail": "Ma'lumot chop etishga chiqarilmagan"}, status=status.HTTP_404_NOT_FOUND)
        if instance.status == "trash":
            return Response({"detail": "Ma'lumot topilmadi"}, status=status.HTTP_404_NOT_FOUND)
        instance.views_count += 1
        instance.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.status = 'trash'
        instance.save()
