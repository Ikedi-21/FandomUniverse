from django.contrib import admin
from .models import Category, Genre, Tag, Content

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    search_fields = ("name", "slug", "description")
    list_filter = ("created_at",)

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")

@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "content_type", "is_published", "view_count", "created_at")
    list_filter = ("content_type", "is_published", "source_type", "category")
    search_fields = ("title", "slug", "description", "category__name")
