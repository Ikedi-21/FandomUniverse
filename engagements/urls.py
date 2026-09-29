from django.urls import path
from . import views

urlpatterns = [
    path('', views.feedback_view, name='feedback'),
    path('bookmarks/', views.bookmark_list, name='bookmark-list'),
    path('bookmarks/toggle/', views.bookmark_toggle, name='bookmark-toggle'),
]
