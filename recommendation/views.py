from rest_framework.response import Response
from rest_framework.decorators import api_view
from recipes.models import Recipe
from recipes.serializers import RecipeSerializer

@api_view(['GET'])
def recommended_recipes(request):
    # 仮：人気順やランダムで取得
    recipes = Recipe.objects.order_by('?')[:5]
    serializer = RecipeSerializer(recipes, many=True, context={"request": request})
    return Response(serializer.data)
