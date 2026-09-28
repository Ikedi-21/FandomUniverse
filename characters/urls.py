from django.urls import path
from . import views

urlpatterns = [
    # /characters/ -> archive grid (character_list).
    path("", views.character_list, name="character-list"),
    # /characters/<id>/ -> single dossier (character_detail).
    path("<int:pk>/", views.character_detail, name="character-detail"),
    # Legacy aliases kept so existing {% url 'list' %} / {% url 'detail' %}
    # references keep resolving while templates migrate to the new names.
    path("", views.character_list, name="list"),
    path("<int:pk>/", views.character_detail, name="detail"),
]
