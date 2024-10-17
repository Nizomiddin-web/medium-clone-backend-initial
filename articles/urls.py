from django.urls import path, include
from rest_framework.routers import DefaultRouter

from articles.views import ArticlesView, TopicFollowView, CreateCommentsView, CommentsView, ArticleDetailCommentsView, \
    FavoriteArticleView, ClapView, ReportArticleView, FAQListView

router = DefaultRouter()
router.register(r'', ArticlesView, basename='articles')
router.register(r'comments', CommentsView, basename='comments')
urlpatterns = [
    path('<int:id>/clap/', ClapView.as_view({'post': 'create', 'delete': 'destroy'}), name='claps'),
    path('<int:id>/comments/', CreateCommentsView.as_view(), name='create-comment'),
    path('<int:id>/detail/comments/', ArticleDetailCommentsView.as_view(), name='article-get-comments'),
    path('<int:id>/favorite/', FavoriteArticleView.as_view(), name='article-favorite'),
    path('<int:id>/report/', ReportArticleView.as_view(), name='article-report'),
    path('topics/<int:id>/follow/', TopicFollowView.as_view(), name='topic-follow'),
    path('faqs/', FAQListView.as_view(), name='faq-list'),
    path('', include(router.urls))
]
