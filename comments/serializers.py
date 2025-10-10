# comments/serializers.py
#コメント作者のアバターURLを返す
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Comment

User = get_user_model()

class CommentAuthorSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "username", "avatar_url"]

    def get_avatar_url(self, obj):
        request = self.context.get("request")
        if obj.avatar:
            return request.build_absolute_uri(obj.avatar.url)
        return request.build_absolute_uri("/static/images/default_avatar.svg")


class CommentSerializer(serializers.ModelSerializer):
    author = CommentAuthorSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "author", "text", "created_at"]
