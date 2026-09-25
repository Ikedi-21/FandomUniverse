# from django.db import models


# # Stores multimedia content available on Fan Hub.
# class Media(models.Model):

#     # Types of media supported by the Multimedia Center.
#     class MediaType(models.TextChoices):
#         VIDEO = "video", "Video"
#         TRAILER = "trailer", "Trailer"
#         AUDIO = "audio", "Audio"
#         PODCAST = "podcast", "Podcast"
#         SOUNDTRACK = "soundtrack", "Soundtrack"
#         ANIMATED_EXPLAINER = "animated_explainer", "Animated Explainer"

#     # Media title.
#     title = models.CharField(max_length=255)

#     # URL-friendly version of the title.
#     slug = models.SlugField(unique=True)

#     # Description of the media.
#     description = models.TextField(blank=True)

#     # Type of media.
#     media_type = models.CharField(
#         max_length=30,
#         choices=MediaType.choices
#     )

#     # URL where the media can be accessed or streamed.
#     media_url = models.URLField()

#     # Preview image for the media.
#     thumbnail = models.ImageField(
#         upload_to="media/thumbnails/",
#         blank=True,
#         null=True
#     )

#     # Category/fandom this media belongs to.
#     category = models.ForeignKey(
#         "catalog.Category",
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name="media_items"
#     )

#     # Tags assigned to the media.
#     tags = models.ManyToManyField(
#         "MediaTag",
#         blank=True,
#         related_name="media_items"
#     )

#     # Indicates whether the media appears as featured content.
#     is_featured = models.BooleanField(default=False)

#     # Allows admins to disable media without deleting it.
#     is_active = models.BooleanField(default=True)

#     # Date the media was created.
#     created_at = models.DateTimeField(auto_now_add=True)

#     # Date the media was last updated.
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return self.title


# # Stores reusable tags for multimedia content.
# class MediaTag(models.Model):

#     # Tag name.
#     name = models.CharField(max_length=50, unique=True)

#     def __str__(self):
#         return self.name


from django.db import models


# Stores ratings submitted by users for media content.
class Rating(models.Model):

    # User who submitted the rating.
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="ratings"
    )

    # Media item being rated.
    media = models.ForeignKey(
        "media_centers.Media",
        on_delete=models.CASCADE,
        related_name="ratings"
    )

    # Rating given by the user, from 1 to 5.
    rating = models.PositiveSmallIntegerField()

    # Date and time when the rating was created.
    created_at = models.DateTimeField(auto_now_add=True)

    # Date and time when the rating was last updated.
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.media.title} - {self.rating}/5"