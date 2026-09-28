from django.urls import path
from . import views

urlpatterns = [
    path('explore/', views.explore, name='explore'),
    # Slug param matches content_detail(request, slug) and every
    # {% url 'content-detail' <slug> %} call site in the templates.
    path('content-detail/<slug:slug>/', views.content_detail, name='content-detail'),
    path('submit-content/', views.submit_content, name='submit-content')
]
