from django.db import models
from django.contrib.auth.models import User


# This is used as a foreign key multiple times to ensure consistency 
class Category(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()

    def __str__(self):
        return self.name

# This is used as a fixed enumeration class to clearly define choices
class ApprovalStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    APPROVED = 'APPROVED', 'Approved'
    REJECTED = 'REJECTED', 'Rejected'

# This is used to capture event highlights
class EventHighlight(models.Model):
    title = models.CharField(max_length=50)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    body = models.TextField()
    event_date = models.DateField()

    # This "eventImages/" folder will be where the images from this model will be stored
    image = models.ImageField(upload_to="eventImages/")
    display_order = models.CharField(max_length=50)

    def __str__(self):
        return self.title

# This is where fanmade posts will be stored
class FanSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    body = models.TextField()

    # This "fanPostImages/" folder will be where the images from this model will be stored
    image = models.ImageField(upload_to="fanPostImages/")

    # The enumeration class is used here
    status = models.CharField(max_length=10, choices=ApprovalStatus.choices, default=ApprovalStatus.PENDING)

    # This will be used by the admin, I left it null with the knowledge that it might take a while before it gets reviewed by an admin
    review_note = models.TextField(blank=True, null=True)
    reviewed_at = models.DateField(blank=True, null=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user}'s {self.title}"