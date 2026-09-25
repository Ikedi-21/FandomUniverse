from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from accounts.models import User

# Create your models here.
class Feedback(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="feedback")
  type = models.CharField(max_length=20, choices=[("bug", "Bug"), ("suggestion", "Suggestion"), ("query", "Query")])
  message = models.TextField()
  status = models.CharField(max_length=20, choices=[("new", "New"), ("in_review", "In_Review"),("resolved", "Resolved")], default="new") 
  admin_response = models.TextField(blank=True)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
      return f"{self.user} "



class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookmarks")

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    target = GenericForeignKey("content_type", "object_id")

    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "content_type", "object_id")

    def __str__(self):
        return f"{self.user} bookmarked {self.target}"