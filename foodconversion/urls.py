from django.urls import path
from . import views

urlpatterns = [
    #単位そのものの換算表を返すための API
    path('unit-conversion/', views.unit_conversion_api, name='unit_conversion_api'),
    #主要食材ごとの cup → g/ml 辞書
    path('ingredient-conversion/', views.ingredient_conversion_api, name='ingredient_conversion_api'),
    path('convert-recipe/', views.convert_recipe, name='convert_recipe'),
]
