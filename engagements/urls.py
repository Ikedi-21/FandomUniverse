from django.urls import path
from . import views

urlpatterns = [
    path('', views.feedback_view, name='feedback'),
    path('feedback/', views.feedback_view, name='feedback-page'),
    path('bookmarks/', views.bookmark_list, name='bookmark-list'),
    path('bookmarks/toggle/', views.bookmark_toggle, name='bookmark-toggle'),
]