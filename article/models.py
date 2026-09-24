from django.db import models

# Create your models here.

class EventHighlight(model.Models):
    title = models.CharField(max_length=50)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    story = models.TextField()
    event_date = models.DateField()
    display_order = models.CharField(max_length=50)

    def __str__(self):
        return self.title

class FanSubmission(model.Models):
    title = models.CharField(max_length=50)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    story = models.TextField()
    event_date = models.DateField()
    display_order = models.CharField(max_length=50)

    def __str__(self):
        return self.title