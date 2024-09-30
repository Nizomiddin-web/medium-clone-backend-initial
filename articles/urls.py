from django.urls import path, include
from rest_framework.routers import DefaultRouter

from articles.views import ArticlesView

router = DefaultRouter()
router.register(r'', ArticlesView, basename='articles')
urlpatterns = [
    path('', include(router.urls))
]
