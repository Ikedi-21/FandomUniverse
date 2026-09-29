from django.contrib import admin
from .models import ActivityLog

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("user", "action", "target_type", "target_id", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("user__username", "target_type", "target_id")
