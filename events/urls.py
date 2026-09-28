from django.urls import path

from . import views

urlpatterns = [
    # Names are intentionally global (no app_name/namespace) because
    # catalog/templates/*.html already reverse 'events'.
    # /events/ -> conventions listing (event_list).
    path("", views.event_list, name="events"),
    # /events/<id>/ -> single convention page (event_detail).
    path("<int:pk>/", views.event_detail, name="event-detail"),
]
