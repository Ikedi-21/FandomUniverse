from django.urls import path
from . import views
from engagements.views import bookmark_list


urlpatterns = [
    path('', views.home, name='home'),
    path('sitemap/', views.sitemap_view, name='sitemap'),
    path('profile/', views.profile_view, name='profile'),
    path('bookmarks/', bookmark_list, name='bookmark-list'),
]
