from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class Role(models.TextChoices):
        USER = "user", "User"
        ADMIN = "admin", "Admin"

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.USER)
    email_verified = models.BooleanField(default=False)
    


class Avatar(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to="avatar_gallery/")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    avatar = models.ForeignKey(Avatar, null=True, blank=True, on_delete=models.SET_NULL)
    custom_avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    bio = models.TextField(blank=True)
    theme = models.CharField(max_length=50, default="dark")
    font_size = models.CharField(max_length=20, default="medium")
    favorite_categories = models.ManyToManyField(
        "catalog.Category", blank=True, related_name="favorite_by_profiles"
    )

    def get_avatar_url(self):
        if self.custom_avatar:
            return self.custom_avatar.url
        if self.avatar:
            return self.avatar.image.url
        return None

    def __str__(self):
        return f"{self.user}'s profile"