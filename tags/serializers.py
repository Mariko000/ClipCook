from rest_framework import serializers
from .models import Tag
from recipes.models import Recipe

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'is_preset']

class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)  # Detail用
    tag_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        write_only=True,
        source='tags'
    )  # 編集・投稿用

    class Meta:
        model = Recipe
        fields = ['id', 'title', 'description', 'author', 'tags', 'tag_ids', 'created_at']
        read_only_fields = ['author', 'created_at']
