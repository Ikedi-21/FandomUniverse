from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from accounts.models import User


class Feedback(models.Model):
    TYPE_CHOICES = [
        ('bug', 'Bug'),
        ('suggestion', 'Suggestion'),
        ('query', 'Query'),
        ('content', 'Content Correction'),
    ]
    SEVERITY_CHOICES = [
        ('low', 'Minor / Cosmetic'),
        ('medium', 'Normal / Functional'),
        ('high', 'Critical / Blocker'),
    ]
    STATUS_CHOICES = [
        ('new', 'New'),
        ('in_review', 'In Review'),
        ('resolved', 'Resolved'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='feedback')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='bug')
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='low')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    admin_response = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.type}] {self.subject} — {self.user}"


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    target = GenericForeignKey('content_type', 'object_id')

    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'content_type', 'object_id')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} bookmarked {self.target or '(deleted)'}"