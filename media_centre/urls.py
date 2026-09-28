from django.urls import path

from . import views

urlpatterns = [
    path("", views.media_list, name="media-list"),
    # POST /media_centre/rate/ -> submit_rating (star widget endpoint).
    path("rate/", views.submit_rating, name="rate-media"),
]
