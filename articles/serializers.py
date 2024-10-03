from rest_framework import serializers
from articles.models import Article, Topic, Clap, Comment
from users.models import CustomUser


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'first_name', 'last_name', 'middle_name', 'email', 'avatar']


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = ['id', 'name', 'description', 'is_active']


class ArticleCreateSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    topic_ids = serializers.PrimaryKeyRelatedField(
        queryset=Topic.objects.all(),
        many=True,
        write_only=True
    )
    topics = TopicSerializer(read_only=True, many=True)

    class Meta:
        model = Article
        fields = ['id', 'author', 'title', 'summary', 'content', 'thumbnail', 'topics', 'topic_ids', 'created_at',
                  'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        topic_ids = validated_data.pop('topic_ids', [])
        if not isinstance(topic_ids, list):
            topic_ids = [topic_ids]
        request = self.context.get('request')
        author = request.user
        article = Article.objects.create(author=author, **validated_data)
        article.topics.set(topic_ids)
        return article


class ClapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clap
        fields = ['user', 'article']


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'user', 'article']


class ArticleDetailSerializer(serializers.ModelSerializer):
    topics = TopicSerializer(many=True, read_only=True)
    author = AuthorSerializer(read_only=True)
    claps = ClapSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = ['id', 'author', 'title', 'summary', 'content', 'status', 'thumbnail', 'views_count', 'reads_count',
                  'created_at', 'updated_at', 'topics', 'claps']


class ArticleListSerializer(serializers.ModelSerializer):
    topics = TopicSerializer(many=True, read_only=True)
    author = AuthorSerializer(read_only=True)
    claps_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Article
        fields = ['id', 'author', 'title', 'summary', 'content', 'status', 'thumbnail', 'views_count', 'reads_count',
                  'created_at', 'updated_at', 'topics', 'comments_count', 'claps_count']

