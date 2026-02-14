# tags/views.py

from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from recipes.models import Recipe
from .serializers import RecipeSerializer, TagSerializer
from .models import Tag
import json
from django.db.models import Q


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().prefetch_related('tags')
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'tags__name']

    # ✅ タグ検索用エンドポイント
    @action(detail=False, methods=['get'])
    def by_tag(self, request):
        tag_name = request.query_params.get('tag', '').strip()
        if not tag_name:
            return Response([])

        # タグが存在する場合のみレシピ抽出
        try:
            tag = Tag.objects.get(name__iexact=tag_name)
        except Tag.DoesNotExist:
            return Response([])

        recipes = Recipe.objects.filter(tags=tag).distinct()
        serializer = self.get_serializer(recipes, many=True)
        return Response(serializer.data)

    # ✅ タイトル or タグ名で検索
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('search', None)

        if search_query:
            # タイトル OR タグ名で検索
            queryset = queryset.filter(
                Q(title__icontains=search_query) | Q(tags__name__icontains=search_query)
            ).distinct()

        return queryset



    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def update(self, request, *args, **kwargs):
        """PATCH / PUTで新規タグ作成＋既存タグ紐付け対応"""
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        data = request.data.copy()

        # JSON文字列として送られてくる可能性に対応
        try:
            new_tag_names = data.pop('new_tags', [])
            if isinstance(new_tag_names, str):
                new_tag_names = json.loads(new_tag_names)
        except json.JSONDecodeError:
            new_tag_names = []

        try:
            tag_ids = data.pop('tag_ids', [])
            if isinstance(tag_ids, str):
                tag_ids = json.loads(tag_ids)
        except json.JSONDecodeError:
            tag_ids = []

        # 一旦タグクリア
        instance.tags.clear()

        # 既存タグを追加
        for tid in tag_ids:
            try:
                tag = Tag.objects.get(id=tid)
                instance.tags.add(tag)
            except Tag.DoesNotExist:
                continue

        # 新規タグを作成して追加
        for name in new_tag_names:
            name = name.strip()
            if not name:
                continue
            tag, _ = Tag.objects.get_or_create(name=name)
            instance.tags.add(tag)

        # 残りのフィールドを更新
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)
