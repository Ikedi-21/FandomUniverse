from django.db import models

# Create your models here.
class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    event_type = models.CharField(max_length=200)
    venue = models.CharField(max_length=200)
    category = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    longitude = models.FloatField()
    latitude = models.FloatField()
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    ticket_link = models.URLField()
    image = models.ImageField(upload_to='events/images')
    def __str__(self):
        return self.title