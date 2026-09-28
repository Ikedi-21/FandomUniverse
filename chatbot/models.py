from django.conf import settings
from django.db import models
from catalog.models import Category


class ChatbotFAQ(models.Model):
    question = models.CharField(max_length=255)
    keyword = models.CharField(
        max_length=255,
        help_text="Comma-separated words people might type, e.g. bookmark, save, favorite",
    )
    answer = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True)  # CHANGED
    is_active = models.BooleanField(default=True)

    def keyword_list(self):                                                                     # CHANGED (new)
        return [k.strip() for k in self.keyword.split(',') if k.strip()]

    def __str__(self):
        return self.question


class ChatbotQuery(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)  # CHANGED
    session_key = models.CharField(max_length=40, blank=True)                                  # CHANGED
    message = models.CharField(max_length=255)
    response = models.TextField()
    matched_faq = models.ForeignKey(ChatbotFAQ, on_delete=models.SET_NULL, blank=True, null=True)         # CHANGED
    created_at = models.DateTimeField(auto_now_add=True)                                       # CHANGED

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.message                                                                     # CHANGED