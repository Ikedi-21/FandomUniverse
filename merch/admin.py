from django.contrib import admin

from .models import Merch, MerchTag


# Store admin: display price and visibility, with searchable tags.
@admin.register(Merch)
class MerchAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "price",
        "is_upcoming",
        "is_published",
        "view_count",
    )
    list_filter = ("category", "is_upcoming", "is_published")
    search_fields = ("name", "franchise", "description", "tags__name")

@admin.register(MerchTag)
class MerchTagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")
