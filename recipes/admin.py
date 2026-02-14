# recipes/admin.py
from django.contrib import admin
from .models import Recipe

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at', 'updated_at')
    list_filter = ('created_at', 'tags')
    search_fields = ('title', 'user__username')
    filter_horizontal = ('tags',)
