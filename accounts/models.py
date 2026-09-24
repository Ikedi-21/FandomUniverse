from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from catalog import Category

# Create your models here.
class User(AbstractUser):
    email = models.EmailField(max_length=254, unique=True)
    role = models.CharField(max_length=50)
    email_verified = models.BooleanField(default=False)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to=None, height_field=None, width_field=None, max_length=None)
    bio = models.CharField(max_length=100)
    theme = models.CharField(max_length=50)
    font_size = models.CharField(max_length=5)
    favorite_categories = models.ManyToManyField(Category)

    