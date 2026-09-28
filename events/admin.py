from django.contrib import admin

from .models import Event


# Convention admin: schedule and visibility at a glance.
@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "city",
        "start_datetime",
        "price",
        "is_published",
    )
    list_filter = ("category", "is_published", "city")
    search_fields = ("title", "description", "venue", "city")
    prepopulated_fields = {"city_slug": ("city",)}
