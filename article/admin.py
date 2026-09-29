from django.contrib import admin
from .models import EventHighlight, FanSubmission

@admin.register(EventHighlight)
class EventHighlightAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "event_date", "display_order")
    list_filter = ("category", "event_date")
    search_fields = ("title", "body", "category__name")

@admin.register(FanSubmission)
class FanSubmissionAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "category", "status", "created_at", "reviewed_by", "reviewed_at")
    list_filter = ("status", "category", "created_at")
    search_fields = ("title", "body", "user__username", "review_note")
