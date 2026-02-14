from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from recipes.models import Recipe
from recipes.serializers import RecipeSerializer
from django.db.models import Q

class RecipeSearchAPIView(APIView):
    """
    /api/search/recipes/?q=検索文字列
    タイトル OR タグ名で検索して JSON 返却
    """
    def get(self, request):
        query = request.query_params.get("q", "").strip()
        if not query:
            return Response([], status=status.HTTP_200_OK)

        recipes = Recipe.objects.filter(
            Q(title__icontains=query) | Q(tags__name__icontains=query)
        ).distinct()

        serializer = RecipeSerializer(recipes, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)
