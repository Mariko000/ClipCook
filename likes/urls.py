from django.urls import path
from .views import toggle_like

urlpatterns = [
    path("toggle/", toggle_like, name="like-toggle"),
]
