from django.urls import path

from . import views

urlpatterns = [
    # POST /media_centre/rate/ -> submit_rating (star widget endpoint).
    path("rate/", views.submit_rating, name="rate-media"),
]
