#recipes/models.py 作ったレシピの写真・メモ記録
from django.db import models
from django.conf import settings
from tags.models import Tag

# Django 5.1 以降は models.JSONField をそのまま使用可能
class Recipe(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)  # レシピ名
    photo = models.ImageField(upload_to="recipes/photos/", blank=True, null=True)  # 写真
    memo = models.TextField(blank=True)  # メモ（作り方や感想など）
    ingredients = models.JSONField(blank=True, default=list)  # 材料の配列
    steps = models.JSONField(blank=True, default=list)  # 作り方手順の配列
    created_at = models.DateTimeField(auto_now_add=True)  # 作成日
    updated_at = models.DateTimeField(auto_now=True)  # 更新日
    tags = models.ManyToManyField(Tag, blank=True, related_name="recipes")

    def __str__(self):
        return self.title

