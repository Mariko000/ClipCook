from django.urls import path
from . import views
from .views import QuantifyView
#サイト全体の共通ロジックを管理
urlpatterns = [
    path('', views.home, name='home'),
    path('quantify/', QuantifyView.as_view(), name='quantify_page'),
]
