from django.urls import path, include
from rest_framework.routers import DefaultRouter

from articles.views import ArticlesView, TopicFollowView

router = DefaultRouter()
router.register(r'', ArticlesView, basename='articles')
urlpatterns = [
    path('topics/<int:id>/follow/', TopicFollowView.as_view(), name='topic-follow'),
    path('', include(router.urls))
]
