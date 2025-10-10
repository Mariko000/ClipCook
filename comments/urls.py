from django.urls import path
from . import views

app_name = 'comments'

urlpatterns = [
    path('add/', views.add_comment, name='add_comment'),
    path('list/', views.list_comments, name='list_comments'),
    path('delete/<int:pk>/', views.delete_comment, name='delete_comment'),
]
