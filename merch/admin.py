from django.contrib import admin

from .models import Merch


# Store admin: stock/price/visibility at a glance, searchable by name.
@admin.register(Merch)
class MerchAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "price",
        "stock",
        "is_upcoming",
        "is_published",
        "view_count",
    )
    list_filter = ("category", "is_upcoming", "is_published")
    search_fields = ("name", "franchise", "description", "tags")
