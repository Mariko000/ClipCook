from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
# 修正: .models から Bookmark モデルをインポート
from .models import Bookmark 
# 【重要】recipes アプリから本物の RecipeSerializer をインポートします
# 実際のファイルパスに合わせてインポート文を調整してください (例: 'recipes.serializers' から)
from recipes.serializers import RecipeSerializer
from recipes.models import Recipe # Recipeモデルも必要

class BookmarkToggleAPIView(APIView):
    """
    ブックマークの追加/削除をトグルするAPIエンドポイント。
    GET: 現在のブックマーク状態をチェックする。
    POST: ブックマークの状態を切り替える。
    """
    permission_classes = [IsAuthenticated]

    def get_content_object(self, request):
        """リクエストパラメータからContent-Typeとオブジェクトを取得するヘルパー"""
        model_name = request.query_params.get('model') or request.data.get('model')
        object_id = request.query_params.get('object_id') or request.data.get('object_id')

        if not model_name or not object_id:
            return None, None
        
        try:
            # model_nameの形式は 'app_name.ModelName' を想定
            app_label, model = model_name.split('.')
            content_type = ContentType.objects.get(app_label=app_label.lower(), model=model.lower())
            
            # content_typeから実際のモデルクラスを取得し、object_idでインスタンスを取得
            model_class = content_type.model_class()
            content_object = get_object_or_404(model_class, pk=object_id)
            
            return content_type, content_object

        except ContentType.DoesNotExist:
            return None, None
        except ValueError:
             # model_name.split('.') でエラー
            return None, None
        except Exception:
            # get_object_or_404 が失敗した場合は既に処理されているため、ここでは他の予期せぬエラーをキャッチ
            return None, None

    def get(self, request, *args, **kwargs):
        """現在のブックマーク状態を返す (Vue側のfetchRecipesで使用)"""
        content_type, content_object = self.get_content_object(request)

        if not content_type or not content_object:
            return Response({'bookmarked': False, 'error': 'Invalid model or object_id'}, status=400)
        
        # 該当するブックマークが存在するかチェック
        bookmarked = Bookmark.objects.filter(
            user=request.user,
            content_type=content_type,
            object_id=content_object.pk
        ).exists()
        
        return Response({'bookmarked': bookmarked})


    def post(self, request, *args, **kwargs):
        """ブックマークの状態をトグルする"""
        content_type, content_object = self.get_content_object(request)

        if not content_type or not content_object:
            return Response({'error': 'Invalid model or object_id'}, status=400)

        # ブックマークの検索
        bookmark, created = Bookmark.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=content_object.pk,
            # defaults={} # createdがTrueの場合の追加フィールドは不要
        )

        if not created:
            # 既に存在していた場合、削除する (トグル)
            bookmark.delete()
            is_bookmarked = False
        else:
            # 新規作成された場合 (ブックマークされた)
            is_bookmarked = True

        return Response({'bookmarked': is_bookmarked})


class BookmarkListAPIView(APIView):
    """
    現在のユーザーがブックマークしたオブジェクト（レシピ）の一覧を返すAPI。
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # レシピモデルのContent-Typeを取得
        try:
            # ContentTypeを取得する際、モデル名が 'Recipe' で app_label が 'recipes' であることを前提とします。
            recipe_content_type = ContentType.objects.get(app_label='recipes', model='recipe')
        except ContentType.DoesNotExist:
            return Response({'error': 'Recipe content type not found. Ensure the "recipes" app is set up correctly.'}, status=500)

        # 現在のユーザーがブックマークしたレシピを取得
        bookmarked_recipes_queryset = Bookmark.objects.filter(
            user=request.user,
            content_type=recipe_content_type
        ).select_related('content_type') 

        # 汎用リレーションを通じて実際のレシピオブジェクトを取得
        recipe_ids = bookmarked_recipes_queryset.values_list('object_id', flat=True)
        
        # Recipeモデルクラス (インポート済み) を使用
        RecipeModel = Recipe 
             
        recipes = RecipeModel.objects.filter(id__in=recipe_ids)
        
        # シリアライズして返却
        # context={'request': request} を渡すことで、get_liked メソッド内で認証済みユーザー情報を利用できるようにする
        serializer = RecipeSerializer(recipes, many=True, context={'request': request}) 
        
        return Response(serializer.data)
