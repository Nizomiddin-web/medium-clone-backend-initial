from django.db.models import Count
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework import generics
from articles.filters import ArticleFilter
from articles.models import Article, Topic, TopicFollow
from articles.permissions import IsOwnerOrReadOnly
from articles.serializers import ArticleCreateSerializer, ArticleDetailSerializer, ArticleListSerializer, \
    TopicSerializer


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
        if self.action in ['create', 'update', 'partial_update']:
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


class TopicFollowView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        topic = get_object_or_404(Topic, id=id)
        user = request.user

        if TopicFollow.objects.filter(user=user, topic=topic).exists():
            return Response(
                {"detail": f"Siz allaqachon '{topic.name}' mavzusini kuzatayapsiz."}, status=status.HTTP_200_OK
            )
        TopicFollow.objects.create(user=user, topic=topic)
        return Response(
            {"detail": f"Siz '{topic.name}' kuzatayapsiz."}, status=status.HTTP_201_CREATED
        )

    def delete(self, request, id):
        topic = get_object_or_404(Topic, id=id)
        if topic:
            user = request.user
            follow = TopicFollow.objects.filter(user=user, topic=topic).first()
            if follow:
                follow.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({
                "detail": f"Siz '{topic.name}' mavzusini kuzatmaysiz."
            }, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "detail": "Hech qanday mavzu berilgan soʻrovga mos kelmaydi."
        }, status=status.HTTP_404_NOT_FOUND)
