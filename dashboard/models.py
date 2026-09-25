from django.db import models
from django.conf import settings
from django.db import models
# Create your models here.

# dashboard	ActivityLog	user (FK, nullable), action
# (viewed, bookmarked, rated, logged_in...), target_type, 
# target_id, created_at. It powers both the "recent activity" 
# on the user dashboard and the admin's active-user stats.

class Actions(models.TextChoices):
    VIEWED = 'VIEWED', 'Viewed'
    BOOKMARKED = 'BOOKMARKED', 'Bookmarked'
    RATED = 'RATED', 'Rated'
    LOGGED_IN = 'LOGGED IN', 'Logged In'

class ActivityLog(models.Model):
    user = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            on_delete=models.SET_NULL,
            null=True,
            blank=True,
            
        )
    action = models.CharField(max_length=10, choices=Actions.choices)
    target_type = models.CharField(max_length=50)
    target_id = models.CharField(max_length=50)
    created_at = models.DateField(auto_now_add=True)
  