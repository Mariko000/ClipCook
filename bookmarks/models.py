from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

User = get_user_model()

class Bookmark(models.Model):
    """
    ユーザーによるオブジェクト（レシピ、記事など）のブックマークを保存するモデル。
    Content-Typeフレームワークを使用して汎用的に対応する。
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookmarks',
        verbose_name='ユーザー'
    )
    
    # Content-Typeフレームワークのフィールド
    content_type = models.ForeignKey(
        ContentType, 
        on_delete=models.CASCADE, 
        verbose_name='コンテンツタイプ'
    )
    object_id = models.PositiveIntegerField(
        verbose_name='オブジェクトID'
    )
    content_object = GenericForeignKey(
        'content_type', 
        'object_id'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='作成日時'
    )

    class Meta:
        verbose_name = 'ブックマーク'
        verbose_name_plural = 'ブックマーク'
        # 同じユーザーが同じオブジェクトを複数回ブックマークできないようにする
        unique_together = ('user', 'content_type', 'object_id')

    def __str__(self):
        return f'{self.user.username} - {self.content_object}'
