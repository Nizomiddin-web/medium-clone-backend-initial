from django.urls import path, include
from rest_framework.routers import DefaultRouter

from articles.views import ArticlesView, TopicFollowView, CreateCommentsView, CommentsView, ArticleDetailCommentsView

router = DefaultRouter()
router.register(r'', ArticlesView, basename='articles')
router.register(r'comments', CommentsView, basename='comments')
urlpatterns = [
    path('<int:id>/comments/', CreateCommentsView.as_view(), name='create-comment'),
    path('<int:id>/detail/comments/', ArticleDetailCommentsView.as_view(), name='article-get-comments'),
    path('topics/<int:id>/follow/', TopicFollowView.as_view(), name='topic-follow'),
    path('', include(router.urls))
]
