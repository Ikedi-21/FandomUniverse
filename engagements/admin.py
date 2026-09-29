from django.contrib import admin
from .models import Bookmark, Feedback

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ("user", "content_type", "object_id", "created_at")
    list_filter = ("content_type", "created_at")
    search_fields = ("user__username", "note")

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("subject", "user", "type", "severity", "status", "created_at")
    list_filter = ("type", "severity", "status", "created_at")
    search_fields = ("subject", "message", "user__username")
