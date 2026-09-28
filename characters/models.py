from django.db import models
from django.utils.text import slugify

# Create your models here.


class Category(models.Model):
    # Fandom grouping for characters (e.g. "Solo Leveling"). slug feeds the
    # ?category=<slug> filter used by character_list and the templates.
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True, null=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        # Auto-fill slug from name on first save; numeric suffix keeps it
        # unique when two fandoms slugify to the same value.
        if not self.slug:
            base = slugify(self.name) or "category"
            unique = base
            counter = 1
            while Category.objects.filter(slug=unique).exclude(pk=self.pk).exists():
                unique = f"{base}-{counter}"
                counter += 1
            self.slug = unique
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class CharacterProfile(models.Model):
    # Character dossier. category must be the local Category above (not
    # catalog's) so the slug filter in views.py resolves correctly.
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="characters")
    name = models.CharField(max_length=150)
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to="characters/", blank=True, null=True)
    source_title = models.CharField(max_length=150, help_text="The fandom or franchise this character is from")
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return self.name