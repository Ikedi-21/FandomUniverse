from django.db import models
from django.utils.text import slugify

# Create your models here.


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True, null=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class CharacterProfile(models.Model):
    # Character categories are seeded alongside catalog fandom categories.
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="characters")
    name = models.CharField(max_length=150)
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to="characters/", blank=True, null=True)
    source_title = models.CharField(max_length=150, help_text="The fandom or franchise this character is from")
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return self.name
