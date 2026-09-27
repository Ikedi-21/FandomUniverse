from django.urls import path
from . import views

urlpatterns = [
    path("", views.character_list, name="list"),
    path("<int:pk>/", views.character_detail, name="detail"),
]
