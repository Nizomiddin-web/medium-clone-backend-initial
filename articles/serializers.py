from rest_framework import serializers
from articles.models import Article, Topic, Clap, Comment
from users.models import CustomUser
from users.serializers import UserSerializer


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
    user = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'article', 'user', 'parent', 'content', 'created_at', 'replies']
        read_only_fields = ['id', 'user', 'article', 'created_at', 'replies']

    def get_replies(self, obj):
        if obj.replies.exists():
            return CommentSerializer(obj.replies.all(), many=True).data
        return []

    def create(self, validated_data):
        request = self.context.get('request')
        id = self.context.get('id')
        try:
            article = Article.objects.get(id=id)
            user = request.user
            comment = Comment.objects.create(user=user, article=article, **validated_data)
            return comment
        except:
            raise serializers.ValidationError({"detail": "Bunday article mavjud emas!"})


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


class ArticleDetailCommentsSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Article
        fields = ['comments']
