from rest_framework.decorators import api_view
from rest_framework.response import Response
from recipes.models import Recipe  # 例：Recipeモデルをソート対象にする
from recipes.serializers import RecipeSerializer

@api_view(['GET'])
def sort_recipes(request):
    sort_by = request.query_params.get('by', 'newest')

    if sort_by == 'likes':
        recipes = Recipe.objects.order_by('-like_count')
    elif sort_by == 'bookmarks':
        recipes = Recipe.objects.order_by('-bookmark_count')
    elif sort_by == 'oldest':
        recipes = Recipe.objects.order_by('created_at')
    else:
        recipes = Recipe.objects.order_by('-created_at')

    serializer = RecipeSerializer(recipes[:50], many=True)
    return Response(serializer.data)
