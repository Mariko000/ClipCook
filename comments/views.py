# comments/views.py
import json
from django.http import JsonResponse
from django.contrib.contenttypes.models import ContentType
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Comment
from .serializers import CommentSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response

# コメント作成（既存の add_comment を拡張、返り値に author 情報を含める）
@require_POST
@login_required
def add_comment(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
    except Exception as e:
        return JsonResponse({"error": "Invalid JSON", "detail": str(e)}, status=400)

    object_id = data.get('object_id')
    content_type_id = data.get('content_type_id')
    text = data.get('text')

    if not all([object_id, content_type_id, text]):
        return JsonResponse({"error": "Missing required fields"}, status=400)

    try:
        content_type = ContentType.objects.get(id=content_type_id)
    except ContentType.DoesNotExist:
        return JsonResponse({"error": "Invalid content_type_id"}, status=400)

    try:
        comment = Comment.objects.create(
            author=request.user,
            content_type=content_type,
            object_id=object_id,
            text=text
        )
        # author の avatar がある場合は絶対 URL を返す
        avatar_url = None
        if getattr(comment.author, "avatar", None):
            try:
                avatar_url = request.build_absolute_uri(comment.author.avatar.url)
            except Exception:
                avatar_url = None

        response = {
            "comment": {
                "id": comment.id,
                "text": comment.text,
                "created_at": comment.created_at.isoformat(),
                "author": {
                    "id": comment.author.id,
                    "username": comment.author.username,
                    "avatar": avatar_url,
                }
            }
        }
        return JsonResponse(response, status=201)
    except Exception as e:
        # サーバログにスタックトレース出す（開発時のみ）
        import traceback
        print(traceback.format_exc())
        return JsonResponse({"error": str(e)}, status=500)


# コメント一覧取得（author情報付き）
@api_view(["GET"])
def list_comments(request):
    object_id = request.GET.get("object_id")
    content_type_id = request.GET.get("content_type_id")

    if not all([object_id, content_type_id]):
        return Response({"error": "Missing required fields"}, status=400)

    try:
        content_type = ContentType.objects.get(id=content_type_id)
    except ContentType.DoesNotExist:
        return Response({"error": "Invalid content_type_id"}, status=400)

    comments = (
        Comment.objects
        .filter(content_type=content_type, object_id=object_id)
        .select_related("author")
        .order_by("-created_at")
    )

    # ✅ ここでシリアライザを呼び出す
    serializer = CommentSerializer(comments, many=True, context={"request": request})

    # ✅ Responseで返す（JsonResponseよりDRF標準的）
    return Response({"comments": serializer.data})

# コメント削除（本人のみ）
@require_POST
@login_required
def delete_comment(request, pk):
    try:
        comment = Comment.objects.get(pk=pk)
    except Comment.DoesNotExist:
        return JsonResponse({"error": "Not found"}, status=404)

    if comment.author != request.user:
        return JsonResponse({"error": "Forbidden"}, status=403)

    comment.delete()
    return JsonResponse({"deleted": True})
