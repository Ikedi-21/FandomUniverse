from django.contrib import admin
from .models import ChatbotFAQ, ChatbotQuery

@admin.register(ChatbotFAQ)
class ChatbotFAQAdmin(admin.ModelAdmin):
    list_display = ("question", "category", "is_active")
    list_filter = ("is_active", "category")
    search_fields = ("question", "keyword", "answer")

@admin.register(ChatbotQuery)
class ChatbotQueryAdmin(admin.ModelAdmin):
    list_display = ("message", "user", "matched_faq", "created_at")
    list_filter = ("created_at",)
    search_fields = ("message", "response", "user__username")
