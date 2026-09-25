from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Profile


# Custom User Admin
@admin.register(User)
class CustomUserAdmin(UserAdmin):

    # Fields displayed in the user list
    list_display = (
        "username",
        "email",
        "role",
        "email_verified",
        "is_active",
        "created_at",
    )

    # Filters available in the sidebar
    list_filter = (
        "role",
        "email_verified",
        "is_active",
    )

    # Fields that can be searched
    search_fields = (
        "username",
        "email",
    )

    # Show newest users first
    ordering = ("-created_at",)

    # Additional fields when viewing/editing a user
    fieldsets = UserAdmin.fieldsets + (
        (
            "Fan Hub Information",
            {
                "fields": (
                    "role",
                    "email_verified",
                    "created_at",
                )
            },
        ),
    )

    # Additional fields when creating a user
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Fan Hub Information",
            {
                "fields": (
                    "email",
                    "role",
                    "email_verified",
                )
            },
        ),
    )


# User Profile Admin
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):

    # Fields displayed in the profile list
    list_display = (
        "user",
        "theme",
        "font_size",
    )

    # Filters
    list_filter = (
        "theme",
        "font_size",
    )

    # Search users by username or email
    search_fields = (
        "user__username",
        "user__email",
    )

    # Makes selecting multiple favorite categories easier
    filter_horizontal = (
        "favorite_categories",
    )