from django.urls import path
from . import views


app_name = "search"

urlpatterns = [
    path('recommended/', views.recommended_recipes, name='recommended_recipes'),

]

