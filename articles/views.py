from tracemalloc import Trace

from django.db.models import Count
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework import generics
from articles.filters import ArticleFilter
from articles.models import Article, Topic, TopicFollow, Comment, Favorite, Clap
from articles.permissions import IsOwnerOrReadOnly, IsOwnerComment
from articles.serializers import ArticleCreateSerializer, ArticleDetailSerializer, ArticleListSerializer, \
    TopicSerializer, CommentSerializer, ArticleDetailCommentsSerializer, ClapSerializer
from users.models import ReadingHistory, Pin


class ArticlesView(ModelViewSet):
    queryset = Article.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ArticleFilter
    lookup_field = 'id'

    @action(detail=True, methods=['post'])
    def read(self, request, id):
        article = get_object_or_404(Article, id=id)
        if article.status == 'publish':
            article.reads_count += 1
            article.save()
            return Response({"detail": "Maqolani o'qish soni ortdi."}, status=status.HTTP_200_OK)
        return Response({"detail": "Not Found."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True,methods=['post'])
    def archive(self,request,id):
        article = get_object_or_404(Article,id=id)
        if article.status=='publish':
            article.status='archive'
            article.save()
            return Response({"detail": "Maqola arxivlandi."},status=status.HTTP_200_OK)
        return Response({"detail":"Not Found."},status=status.HTTP_404_NOT_FOUND)

    @action(detail=True,methods=['post'])
    def pin(self,request,id):
        article = get_object_or_404(Article,id=id)
        print(article)
        if article.status=='publish':
            user = request.user
            print(user)
            if not Pin.objects.filter(user=user,article=article).exists():
                Pin.objects.create(user=user,article=article)
                return Response({"detail": "Maqola pin qilindi."},status=status.HTTP_200_OK)
            return Response({"detail":"Maqola Pin qilingan"},status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail":"Article not published"},status=status.HTTP_404_NOT_FOUND)

    @action(detail=True,methods=['delete'])
    def unpin(self,request,id):
        article = get_object_or_404(Article,id=id)
        if article.status=='publish':
            if Pin.objects.filter(user=request.user,article=article).exists():
                pin = Pin.objects.get(user=request.user,article=article)
                pin.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({"detail":"Maqola topilmadi.."},status=status.HTTP_404_NOT_FOUND)
        return Response({"detail":"Article not published"},status=status.HTTP_404_NOT_FOUND)

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

    def get_permissions(self):
        is_author_article = self.request.query_params.get('is_author_article')
        if is_author_article:
            return [IsAuthenticated()]
        if self.action in ['pin','unpin']:
            permission_classes=[IsAuthenticated]
        else:
            permission_classes=[IsOwnerOrReadOnly]
        return [permission() for permission in permission_classes]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status == "pending":
            return Response({"detail": "Ma'lumot chop etishga chiqarilmagan"}, status=status.HTTP_404_NOT_FOUND)
        if instance.status == "trash":
            return Response({"detail": "Ma'lumot topilmadi"}, status=status.HTTP_404_NOT_FOUND)
        instance.views_count += 1
        instance.save()
        if not ReadingHistory.objects.filter(user=request.user, article=instance).exists():
            ReadingHistory.objects.create(user=request.user, article=instance)
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


class FavoriteArticleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        article = get_object_or_404(Article, id=id)
        user = request.user

        if article:
            if Favorite.objects.filter(user=user, article=article).exists():
                return Response({"detail": "Maqola sevimlilarga allaqachon qo'shilgan."},
                                status=status.HTTP_400_BAD_REQUEST)
            Favorite.objects.create(user=user, article=article)
            return Response({"detail": "Maqola sevimlilarga qo'shildi."}, status=status.HTTP_201_CREATED)

        return Response({"detail": "Maqola topilmadi."}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, id):
        article = get_object_or_404(Article, id=id)
        user = request.user
        if article:
            favorite = Favorite.objects.filter(user=user, article=article).first()
            if favorite:
                favorite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "Maqola topilmadi."}, status=status.HTTP_404_NOT_FOUND)


class ClapView(ModelViewSet):
    serializer_class = ClapSerializer
    queryset = Clap.objects.all()
    http_method_names = ['post', 'delete']
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def create(self, request, *args, **kwargs):
        id = kwargs.get('id')
        try:
            article = Article.objects.get(id=id)
            if article.status != 'publish':
                return Response({"detail": "clap bosish uchun maqola statusi 'publish' bo'lishi kerak."},
                                status=status.HTTP_404_NOT_FOUND)
            serializer = self.get_serializer(data=request.data, context={'request': request, 'id': id})
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except:
            return Response({"detail": "Maqola topilmadi."}, status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, *args, **kwargs):
        id = kwargs.get('id')
        try:
            article = Article.objects.get(id=id)
            if article.status != 'publish':
                return Response({"detail": "clap bosish uchun maqola statusi 'publish' bo'lishi kerak."},
                                status=status.HTTP_404_NOT_FOUND)
            user = request.user
            clap = article.claps.filter(user=user).first()
            if clap:
                self.perform_destroy(clap)
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({"detail": "'Not found."},
                            status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({"detail": "Maqola topilmadi."}, status=status.HTTP_404_NOT_FOUND)
