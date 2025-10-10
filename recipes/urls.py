# recipes/urls.py
from rest_framework.routers import DefaultRouter
from .views import RecipeViewSet
from django.urls import path, include

app_name = "recipes"

router = DefaultRouter()
router.register(r"recipes", RecipeViewSet, basename="recipe")  # ← この一行で、
# /api/recipes/ と /api/recipes/<id>/ の両方が自動生成されます。

urlpatterns = [
    path("", include(router.urls)),
]
