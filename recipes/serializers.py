import json
from rest_framework import serializers
from .models import Recipe
from likes.models import Like
from django.contrib.contenttypes.models import ContentType

class RecipeSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    like_count = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        # ingredients と steps を JSONField として扱う
        fields = ["id", "user", "title", "photo", "memo", "ingredients", "steps", "created_at", "like_count", "liked"]
        read_only_fields = ["id", "user", "created_at"]

    def get_like_count(self, obj):
        content_type = ContentType.objects.get_for_model(Recipe)
        return Like.objects.filter(content_type=content_type, object_id=obj.id).count()

    def get_liked(self, obj):
        user = self.context["request"].user
        if not user.is_authenticated:
            return False
        content_type = ContentType.objects.get_for_model(Recipe)
        return Like.objects.filter(
            user=user,
            content_type=content_type,
            object_id=obj.id
        ).exists()

    def update(self, instance, validated_data):
        # ingredients/steps が multipart のとき文字列で来る可能性を考慮
        ingredients = validated_data.pop("ingredients", instance.ingredients)
        steps = validated_data.pop("steps", instance.steps)

        # JSON文字列で来ていたらパース
        if isinstance(ingredients, str):
            try:
                ingredients = json.loads(ingredients)
            except Exception:
                # 万が一 JSON でなければ改行で分割して配列にするフォールバック
                ingredients = [line.strip() for line in ingredients.splitlines() if line.strip()]

        if isinstance(steps, str):
            try:
                steps = json.loads(steps)
            except Exception:
                steps = [line.strip() for line in steps.splitlines() if line.strip()]

        # title を取り出す（popしておくと後続ループで重複しない）
        title = validated_data.pop("title", instance.title)

        # フロントと同一の区切り語を使って memo を再構築
        memo_lines = []
        memo_lines.append(f"=== {title} ===")
        if ingredients:
            memo_lines.append("=== 材料 ===")
            memo_lines.extend(ingredients)
        if steps:
            memo_lines.append("=== 作り方 ===")   # ← ここを "作り方" にする（フロントで期待）
            memo_lines.extend(steps)

        # インスタンスに反映
        instance.title = title
        instance.ingredients = ingredients
        instance.steps = steps
        instance.memo = "\n".join(memo_lines)

        # 残りの validated_data（photo など）も更新
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance