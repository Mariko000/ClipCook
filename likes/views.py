from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.contenttypes.models import ContentType
from .models import Like
from recipes.models import Recipe

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def toggle_like(request):
    model = request.data.get("model") if request.method == "POST" else request.query_params.get("model")
    object_id = request.data.get("object_id") if request.method == "POST" else request.query_params.get("object_id")

    if model != "recipes.Recipe":
        return Response({"error": "Unsupported model"}, status=400)

    content_type = ContentType.objects.get_for_model(Recipe)
    try:
        obj = Recipe.objects.get(id=object_id)
    except Recipe.DoesNotExist:
        return Response({"error": "Recipe not found"}, status=404)

    # POST → いいねトグル
    if request.method == "POST":
        like, created = Like.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=obj.id,
        )

        if not created:
            like.delete()
            liked = False
        else:
            liked = True
    else:
        # GET → 初期状態確認
        liked = Like.objects.filter(
            user=request.user,
            content_type=content_type,
            object_id=obj.id,
        ).exists()

    like_count = Like.objects.filter(content_type=content_type, object_id=obj.id).count()

    return Response({
        "liked": liked,
        "like_count": like_count,
        "object_id": obj.id,
    })
