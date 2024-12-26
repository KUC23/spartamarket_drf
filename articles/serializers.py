# articles/serializers.py
from rest_framework import serializers
from .models import Article


class ArticleListSerializer(serializers.ModelSerializer):
    """게시글 목록 죄회 Serializer"""

    class Meta:
        model = Article
        fields = ('id', 'author', 'title', 'created_at', 'view_count')  # 조회수 필드 추가
        read_only_fields = ('author', )
        
        
class ArticleDetailSerializer(serializers.ModelSerializer):
    """게시글 상세 조회 및 생성 Serializer"""
    author = serializers.ReadOnlyField(source='author.email') # author 필드에 작성자의 이메일만 출력
    
    class Meta:
        model = Article
        fields = ('id', 'author', 'title', 'content', 'created_at', 'updated_at', 'view_count')  # 조회수 필드 추가

from .models import Comment
class CommentSerializer(serializers.ModelSerializer):
    """댓글 조회 및 생성 Serializer"""
    author = serializers.ReadOnlyField(source='author.email')
    like_count = serializers.IntegerField(source='like_users.count', read_only=True)
    is_liked = serializers.SerializerMethodField() #좋아요 여부
    
    class Meta:
        model = Comment
        fields = ('id', 'article', 'author', 'content', 'created_at', 
                 'updated_at', 'like_users', 'like_count', 'is_liked')
        read_only_fields = ('article',)
        
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.like_users.filter(pk=request.user.pk).exists()
        return False