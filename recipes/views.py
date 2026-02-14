from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied

# BasePermission, SAFE_METHODS, IsAuthenticatedをインポートに追加
from rest_framework.permissions import IsAuthenticatedOrReadOnly, BasePermission, SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets, permissions
from .models import Recipe
from .serializers import RecipeSerializer
from django.contrib.auth import get_user_model
import json
from tags.models import Tag

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_recipes(request):
    """
    ログインユーザー本人のレシピのみ返す
    """
    user = request.user
    recipes = Recipe.objects.filter(user=user).order_by("-created_at")
    serializer = RecipeSerializer(recipes, many=True, context={"request": request})
    return Response(serializer.data)


# =================================================================
# 1. カスタムパーミッション: オーナーシップチェック
# =================================================================
class IsOwnerOrReadOnly(BasePermission):
    """
    オブジェクトのオーナーのみが編集/削除を許可されるカスタムパーミッション。
    読み取り操作 (GET, HEAD, OPTIONS) は誰でも許可します。
    """
    def has_object_permission(self, request, view, obj):
        # 読み取り操作 (GET, HEAD, OPTIONS) は常に許可
        if request.method in SAFE_METHODS:
            return True
        
        # 書き込み操作 (PUT, PATCH, DELETE) はオブジェクトのオーナーのみに許可
        return obj.user == request.user

# =================================================================
# 2. RecipeViewSet: パーミッションを動的に設定
# =================================================================
class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by("-created_at")
    serializer_class = RecipeSerializer

    def get_permissions(self):
        from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
        from .views import IsOwnerOrReadOnly

        if self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
        elif self.action == 'create':
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsAuthenticatedOrReadOnly]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        recipe = serializer.save(user=self.request.user)

    # ---- 修正版 ----
        raw_tag_ids = self.request.data.get("tag_ids", "[]")
        try:
            tag_ids = json.loads(raw_tag_ids) if isinstance(raw_tag_ids, str) else raw_tag_ids
        except json.JSONDecodeError:
            tag_ids = []

        raw_new_tags = self.request.data.get("new_tags", "[]")
        try:
             new_tag_names = json.loads(raw_new_tags) if isinstance(raw_new_tags, str) else raw_new_tags
        except json.JSONDecodeError:
             new_tag_names = []

        tags_to_set = []

    # 既存タグを追加
        if tag_ids:
            tags_to_set.extend(Tag.objects.filter(id__in=tag_ids))

    # 新規タグを作成
        for name in new_tag_names:
           if name.strip():
            tag, created = Tag.objects.get_or_create(name=name.strip())
            tags_to_set.append(tag)

    # ManyToMany を set() で紐付け
        if tags_to_set:
            recipe.tags.set(tags_to_set)

# 既存の recipe_list 関数 (通常はViewSetが代用するため不要だが残す)
@api_view(["GET"])
@permission_classes([IsAuthenticatedOrReadOnly])
def recipe_list(request):
    recipes = Recipe.objects.all().order_by("-created_at")
    serializer = RecipeSerializer(recipes, many=True, context={"request": request})
    return Response(serializer.data)
