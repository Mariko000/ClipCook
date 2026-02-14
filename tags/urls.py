from django.urls import path
from .views import TagViewSet, RecipeViewSet

urlpatterns = [
    # Recipe
    path('recipes/', RecipeViewSet.as_view({'get': 'list', 'post': 'create'}), name='recipe-list'),
    path('recipes/<int:pk>/', RecipeViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='recipe-detail'),

    # Tag
    path('tags/', TagViewSet.as_view({'get': 'list', 'post': 'create'}), name='tag-list'),
    path('tags/<int:pk>/', TagViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='tag-detail'),
]
