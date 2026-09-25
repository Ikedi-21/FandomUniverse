from django.contrib import admin

from .models import Rating


# Register the Rating model
@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):

    # Fields displayed in the rating list
    list_display = (
        "user",
        "media",
        "rating",
        "created_at",
        "updated_at",
    )

    # Filters available in the sidebar
    list_filter = (
        "rating",
        "created_at",
    )

    # Search ratings by username, email, or media title
    search_fields = (
        "user__username",
        "user__email",
        "media__title",
    )

    # Show newest ratings first
    ordering = ("-created_at",)