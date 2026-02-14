"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# プロジェクトルート上のurls.py
import os
from django.contrib import admin
from . import views
from django.urls import path, include, re_path
from core import views as core_views # coreアプリのビューをインポート
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.views.static import serve
from core.views import QuantifyView

urlpatterns = [
    path('', core_views.home, name='home'),
    path('about/', views.about_page, name='about_page'),
    path('explained_design/', views.explained_design, name='explained_design'),
    path('my_skills/', views.my_skills, name='my_skills'),
    path('admin/', admin.site.urls),
    # allauthのURL設定をインクルード
    path('accounts/', include('allauth.urls')),
    # ユーザー関連のHTMLページを管理
    path('users/', include('users.urls')),
    # ユーザー関連のAPIエンドポイントを管理
    path('api/users/', include('users.api.urls')),

    path('blog/', include('blog.urls')),
   
    path('api/likes/', include('likes.urls')),      # いいね機能のAPIエンドポイント設置
    path('comments/', include('comments.urls')),
    path("api/", include("comments.urls")),  # コメント機能のAPIエンドポイント設置

    path('contact/', include('contact.urls')),
    path("api/search/", include("search.urls", namespace="search")),

    path("messengers/", include("messengers.urls")), 

    
    # フォロー関連のAPIエンドポイントを管理
    path('api/followers/', include('followers.urls')),

    # 食材の単位を変換するアプリの関連のAPIエンドポイントを管理
    path('api/foodconversion/', include('foodconversion.urls')),
    # レシピの保存
    path("api/", include("recipes.urls")),

    # ブックマーク
    path('api/bookmarks/', include('bookmarks.urls')),
    # おすすめレシピ
    path('api/recommendation/', include('recommendation.urls')),
    #レシピのフィルター
    path('api/sorts/', include('sorts.urls')),
    #tag
    path('api/', include('tags.urls')),

    # Vue SPA 専用ページ
     #/quantify/ 以下はすべて QuantifyView（vue_app.html）に任せる
    re_path(r'^quantify/.*$', QuantifyView.as_view(), name='quantify_page'),

    # path('', include('core.urls')),  # core.urls に /quantify/ が含まれる

     # Service Worker をルートに置く
     # static, media など必要に応じてここに追加
    path('sw.js', lambda request: serve(
        request,
        'sw.js',
        document_root=os.path.join(settings.BASE_DIR, 'static/vue')
    )),
    path('workbox-4c320e2c.js', lambda request: serve(
        request,
        'workbox-4c320e2c.js',
        document_root=os.path.join(settings.BASE_DIR, 'static/vue')
    )),



]

# メディアファイルを開発環境で配信する設定
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
