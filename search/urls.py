from django.urls import path
from .views import RecipeSearchAPIView 

app_name = "search"

urlpatterns = [
    path("recipes/", RecipeSearchAPIView.as_view(), name="recipe-search"),
]
