from django.urls import path
from . import views

urlpatterns = [
    path('explore/', views.explore, name='explore'),
    path('content-detail/', views.content_detail, name='content-detail'),
    path('submit-content/', views.submit_content, name='submit-content')
]
