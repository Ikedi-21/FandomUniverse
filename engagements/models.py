from django.db import models
from django.contrib.auth import get_user_model
from accounts import User

# Create your models here.
class Feedback(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="feedback")
  type = models.CharField(max_length=20, choices=[("bug", "Bug"), ("suggestion", "Suggestion"), ("query", "Query")])
  message = models.TextField()
  status = models.CharField(max_length=20, choices=[("new", "New"), ("in_review", "In_Review"),("resolved", "Resolved")], default="new") 
  admin_response = models.TextField(blank=True)
  created_at = models.DateTimeField(auto_now_add=True)