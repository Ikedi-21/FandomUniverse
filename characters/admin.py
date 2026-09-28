from django.contrib import admin
from .models import Category, CharacterProfile

# Register your models here.


# Fandom admin: slug auto-fills from name via prepopulated_fields.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


# Dossier admin: publish toggle per character, filterable by fandom.
@admin.register(CharacterProfile)
class CharacterProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "source_title", "is_published")
    list_filter = ("category", "is_published")
    search_fields = ("name", "source_title", "bio")