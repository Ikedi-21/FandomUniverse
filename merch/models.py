from django.db import models

# Create your models here.
class Merch(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    tags = models.CharField(max_length=200)
    category = models.CharField(max_length=200)
    is_upcoming = models.BooleanField(default=False)
    release_date = models.DateTimeField()
    view_count = models.IntegerField(default=0)
    image = models.ImageField(upload_to='merch/images')
    def __str__(self):
        return self.name