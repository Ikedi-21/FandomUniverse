# catalog/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('explore/', views.explore, name='explore'),
    path('content/<slug:slug>/', views.content_detail, name='content-detail'),
    path('submit-content/', views.submit_content, name='submit-content'),
]