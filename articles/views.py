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
from articles.models import Article, Topic, TopicFollow, Comment
from articles.permissions import IsOwnerOrReadOnly, IsOwnerComment
from articles.serializers import ArticleCreateSerializer, ArticleDetailSerializer, ArticleListSerializer, \
    TopicSerializer, CommentSerializer, ArticleDetailCommentsSerializer


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


class CreateCommentsView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    queryset = Comment
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        id = kwargs.get('id')
        try:
            article = Article.objects.get(id=id)
            if article.status != "publish":
                return Response({"detail": "Izoh yozish uchun maqola statusi 'publish' bo'lishi kerak."},
                                status=status.HTTP_404_NOT_FOUND)
            serializer = self.get_serializer(data=request.data, context={'id': id, 'request': request})
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Article.DoesNotExist:
            return Response({"detail": 'No Article matches the given query.'}, status=status.HTTP_404_NOT_FOUND)


class CommentsView(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerComment]
    http_method_names = ['patch', 'delete']


class ArticleDetailCommentsView(generics.RetrieveAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleDetailCommentsSerializer
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        response_data = {
            "count": 1,
            "next": None,
            "previous": None,
            "results": [
                {
                    "comments": serializer.data['comments']
                }
            ]
        }
        return Response(response_data)
