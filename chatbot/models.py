from django.db import models
from accounts import User
from catalog import Category


class ChatbotFAQ(models.Model):
    question = models.CharField(max_length=255)
    keyword = models.CharField(max_length=255)
    answer = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.question


class ChatbotQuery(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    session_key = models.CharField(max_length=10)
    message = models.CharField(max_length=255)
    response = models.TextField()
    matched_faq = models.ForeignKey(ChatbotFAQ, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return {self.message}