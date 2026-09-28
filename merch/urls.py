from django.urls import path

from . import views

urlpatterns = [
    # Names are intentionally global (no app_name/namespace) because
    # catalog/templates/*.html already reverse 'merch-list'.
    # /merch/ -> storefront grid (merch_list).
    path("", views.merch_list, name="merch-list"),
    # /merch/<id>/ -> single product page (merch_detail).
    path("<int:pk>/", views.merch_detail, name="merch-detail"),
]
