import os
import django
import requests
from django.core.files.base import ContentFile

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from recipes.models import Recipe
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(username="mariko")

image_url = "http://127.0.0.1:8000/media/recipes/photos/hotcake_zmnO5Pk.jpeg"
image_content = requests.get(image_url).content

for i in range(8):
    recipe = Recipe(
        user=user,
        title=f"テストレシピ{i+1}",
        memo=f"これはテスト用のレシピです {i+1}"
    )
    recipe.photo.save(f"dummy{i+1}.jpeg", ContentFile(image_content), save=True)

print("8 件のテストレシピを生成しました。")
