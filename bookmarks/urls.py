from django.urls import path
from .views import BookmarkToggleAPIView, BookmarkListAPIView 

urlpatterns = [
    # Vue.js側でaxiosがアクセスするパス: http://127.0.0.1:8000/api/bookmarks/toggle/
    path('toggle/', BookmarkToggleAPIView.as_view(), name='bookmark_toggle'),

    # http://127.0.0.1:8000/api/bookmarks/list/
    path('list/', BookmarkListAPIView.as_view(), name='bookmark_list'),
]
