from django.db import models
from django.utils.text import slugify

# Create your models here.
"""
catalog	Category	name, slug, description, cover_image
catalog	Genre	name, slug
catalog	Tag	name, slug
catalog	Content	category (FK), title, type (article/video/audio/image), description, body (rich text, for articles), genres (M2M), tags (M2M), release_date, popularity_score, view_count, thumbnail, source_type (embed/upload), video_url or file, is_published, created_by, created_at
"""

class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    cover_image = models.ImageField(upload_to='categories/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
class Genre(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    
class Tag(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    
class Content(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='contents')
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES, default='article')
    
    description = models.TextField(blank=True, null=True)
    body = models.TextField(blank=True, null=True, help_text="Rich text content for articles")
    
    genres = models.ManyToManyField(Genre, blank=True, related_name='contents')
    tags = models.ManyToManyField(Tag, blank=True, related_name='contents')
    
    release_date = models.DateTimeField(blank=True, null=True)
    popularity_score = models.FloatField(default=0.0)
    view_count = models.PositiveIntegerField(default=0)
    
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES, default='upload')
    video_url = models.URLField(blank=True, null=True, help_text="Used if source_type is embed")
    file = models.FileField(upload_to='content_files/', blank=True, null=True, help_text="Used if source_type is upload")
    
    is_published = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_contents')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
