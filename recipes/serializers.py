import json
from rest_framework import serializers
from .models import Recipe
from likes.models import Like
from django.contrib.contenttypes.models import ContentType
from tags.models import Tag

# --------------------------------------------------------------------
# 💡 [NEW] Base64エンコードされた画像を受け入れるカスタムフィールド
# --------------------------------------------------------------------
from rest_framework.fields import ImageField
import base64
import six
import uuid
from django.core.files.base import ContentFile

class Base64ImageField(ImageField):
    """
    Base64文字列として画像データを受け入れるカスタム ImageField。
    """
    def to_internal_value(self, data):
        # Base64文字列ではない場合は、通常のImageFieldの処理に任せる
        if isinstance(data, six.string_types) and data.startswith('data:image'):
            # 例: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgA...'
            format, imgstr = data.split(';base64,') 
            ext = format.split('/')[-1] # 拡張子を取得

            # Base64文字列をデコード
            data = ContentFile(base64.b64decode(imgstr), name=f'{uuid.uuid4()}.{ext}')
        
        return super().to_internal_value(data)
    
# --------------------------------------------------------------------
# JSON文字列をリストにデシリアライズするためのカスタムフィールド (修正箇所)
# --------------------------------------------------------------------
class JSONStringListField(serializers.ListField):
    """
    FormDataでJSON文字列として渡された配列データを、内部的にPythonのリストに変換する。
    multipart/form-dataでのDRFの挙動（文字列が1要素のリストとして入ってくる）にも対応。
    """
    def to_internal_value(self, data):
        # 💡 [修正箇所] データが None または空文字列の場合、空リストとして処理
        if data is None or data == '':
            return []
            
        # 1. データが文字列の場合 (例: "[\"a\", \"b\"]")
        if isinstance(data, str):
            try:
                data = json.loads(data)
                # JSONとしてパースしたが、それがリストではなかった場合（例: "{}"）は、そのままリストの要素として処理
                if not isinstance(data, list):
                    data = [data]
            except json.JSONDecodeError:
                # JSONではない場合は、そのままリストの要素として処理させる
                data = [data]
        
        # 2. データが1要素のリストで、その要素がJSON文字列の場合 (multipart/form-data対策)
        # このパスは、フロントから tag_ids: ["[]"] のように送られた場合に対応する
        elif isinstance(data, list) and len(data) == 1 and isinstance(data[0], str):
            try:
                # 最初の要素をJSONとしてパース
                parsed_data = json.loads(data[0])
                if isinstance(parsed_data, list):
                    # パース結果がリストであれば、それを新しいデータとして採用
                    data = parsed_data
            except json.JSONDecodeError:
                pass # パースに失敗したら、そのままのリスト ([文字列]) で続行
        
        # dataがリストになったことを期待して、親クラスのバリデーションに渡す
        return super().to_internal_value(data)



class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "is_preset"]


class RecipeSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    like_count = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    # 💡 tag_ids, ingredients, steps にカスタムフィールドを適用
    tag_ids = JSONStringListField(
        child=serializers.IntegerField(), 
        source="tags",
        write_only=True,
        required=False
    )
    ingredients = JSONStringListField(
        child=serializers.CharField(),
        required=False
    )
    steps = JSONStringListField(
        child=serializers.CharField(),
        required=False
    )
    
    new_tags = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )

    # 💡 photo フィールドを Base64 対応のカスタムフィールドに置き換え
    photo = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = [
            "id", "user", "title", "photo", "memo",
            "ingredients", "steps", "created_at",
            "like_count", "liked", "tags", "tag_ids", "new_tags"
        ]
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
    
    def create(self, validated_data):
        # tags/new_tags の処理を create にも追加し、tag_ids から tags に戻す
        tag_ids = validated_data.pop("tags", []) # tag_ids は source="tags" のため tags として pop
        new_tag_names = validated_data.pop("new_tags", [])
        
        # memo の作成ロジックを create に移動
        title = validated_data.get("title", "")
        ingredients = validated_data.get("ingredients", [])
        steps = validated_data.get("steps", [])
        
        # 💡 [修正] ingredients/steps が空の文字列をフィルタリング
        ingredients = [item for item in ingredients if item.strip()]
        steps = [item for item in steps if item.strip()]
        
        memo_lines = [f"=== {title} ==="]
        if ingredients:
            memo_lines.append("=== 材料 ===")
            memo_lines.extend(ingredients)
        if steps:
            memo_lines.append("=== 作り方 ===")
            memo_lines.extend(steps)
        validated_data["memo"] = "\n".join(memo_lines)
        
        # レシピ作成
        recipe = Recipe.objects.create(**validated_data)
        
        # タグ処理
        tags_to_set = list(tag_ids)
        for name in new_tag_names:
            if name.strip():
                tag, created = Tag.objects.get_or_create(name=name.strip())
                tags_to_set.append(tag)

        if tags_to_set:
            recipe.tags.set(tags_to_set)
        
        return recipe


    def update(self, instance, validated_data):
        # タグ情報を事前に取得
        tag_objs = validated_data.pop("tags", [])
        new_tag_names = validated_data.pop("new_tags", [])

        # ingredients / steps 処理（従来通り）
        ingredients = validated_data.pop("ingredients", instance.ingredients)
        steps = validated_data.pop("steps", instance.steps)

        if isinstance(ingredients, str):
            try:
                ingredients = json.loads(ingredients)
            except Exception:
                ingredients = [line.strip() for line in ingredients.splitlines() if line.strip()]

        if isinstance(steps, str):
            try:
                steps = json.loads(steps)
            except Exception:
                steps = [line.strip() for line in steps.splitlines() if line.strip()]

        title = validated_data.pop("title", instance.title)

        # memo 再構築
        memo_lines = [f"=== {title} ==="]
        if ingredients:
            memo_lines.append("=== 材料 ===")
            memo_lines.extend(ingredients)
        if steps:
            memo_lines.append("=== 作り方 ===")
            memo_lines.extend(steps)

        instance.title = title
        instance.ingredients = ingredients
        instance.steps = steps
        instance.memo = "\n".join(memo_lines)

        # その他のフィールドを更新
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        # タグ処理
        tags_to_set = list(tag_objs)
        for name in new_tag_names:
            if name.strip():
                tag, created = Tag.objects.get_or_create(name=name.strip())
                tags_to_set.append(tag)

        if tags_to_set:
            instance.tags.set(tags_to_set)
        else:
            instance.tags.clear()

        instance.save()
        return instance
