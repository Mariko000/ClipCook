# recipes/urls.py
from rest_framework.routers import DefaultRouter
from .views import RecipeViewSet, my_recipes
from django.urls import path, include

app_name = "recipes"

router = DefaultRouter()
router.register(r"recipes", RecipeViewSet, basename="recipe")  # ← この一行で、
# /api/recipes/ と /api/recipes/<id>/ の両方が自動生成されます。

urlpatterns = [
    path("", include(router.urls)),
    path("my_recipes/", my_recipes, name="my_recipes"),  # ← Album.vue で「ログインユーザー本人が投稿したレシピのみ」を表示
]
