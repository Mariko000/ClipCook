from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied

# ★修正: BasePermission, SAFE_METHODS, IsAuthenticatedをインポートに追加
from rest_framework.permissions import IsAuthenticatedOrReadOnly, BasePermission, SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets, permissions
from .models import Recipe
from .serializers import RecipeSerializer
from django.contrib.auth import get_user_model

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
    
    # ★修正: permission_classesの静的な定義を削除し、get_permissionsで動的に設定する
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly] # ← この行は削除（またはコメントアウト）

    # ★追加: get_permissions メソッド
    def get_permissions(self):
        """
        リクエストのメソッドとアクションに基づいてパーミッションを動的に設定する。
        """
        # 更新 ('update'/'partial_update') および削除 ('destroy') の場合
        if self.action in ['update', 'partial_update', 'destroy']:
            # ログイン済み (IsAuthenticated) かつ オーナーであること (IsOwnerOrReadOnly) を要求
            self.permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
        
        # 新規作成 ('create') の場合
        elif self.action == 'create':
            # ログインユーザーのみ許可
            self.permission_classes = [IsAuthenticated]
        
        # リスト取得 ('list') や詳細閲覧 ('retrieve') の場合 (デフォルト)
        else:
            # 認証済みでなくても読み取り専用で許可
            self.permission_classes = [IsAuthenticatedOrReadOnly]
            
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
       if self.request.user.is_authenticated:
        serializer.save(user=self.request.user)
       else:
        raise PermissionDenied("ログインユーザーのみレシピを作成できます。")




# 既存の recipe_list 関数 (通常はViewSetが代用するため不要だが残す)
@api_view(["GET"])
@permission_classes([IsAuthenticatedOrReadOnly])
def recipe_list(request):
    recipes = Recipe.objects.all().order_by("-created_at")
    serializer = RecipeSerializer(recipes, many=True, context={"request": request})
    return Response(serializer.data)
