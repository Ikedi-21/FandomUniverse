from django.db import models


class Event(models.Model):
    """Convention / expo listing for the Events & Cons page.

    Source design: ``characters/templates/events.html`` (filter bar, event
    cards, interactive map pins, venue panel, ticket modal).
    """

    # Store categories matching the prototype filter pills.
    CATEGORY_CHOICES = [
        ("anime", "Anime Cons"),
        ("gaming", "Gaming Expos"),
        ("comics", "Comic Cons"),
    ]

    # Identity: title, blurb, type (convention/expo/summit...), and the
    # category driving the anime / gaming / comics filter.
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    event_type = models.CharField(max_length=200, blank=True)
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, default="anime"
    )
    # Short key bridging a DB row to its static map pin / venue entry
    # (e.g. "ax", "gamescom", "tgs"). Must be unique when set.
    map_code = models.SlugField(max_length=50, unique=True, blank=True, null=True)

    # Place and time. city holds the display name ("Los Angeles, USA");
    # city_slug is the filter key ("los-angeles"). Coordinates are
    # optional (used if the map ever plots pins from the DB).
    venue = models.CharField(max_length=200)
    venue_address = models.CharField(max_length=255, blank=True)
    # Transit / airport / hotel notes shown in the venue panel (HTML ok).
    venue_info = models.TextField(blank=True)
    city = models.CharField(max_length=200)
    city_slug = models.SlugField(max_length=100, blank=True)
    longitude = models.FloatField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    start_datetime = models.DateTimeField(blank=True, null=True)
    end_datetime = models.DateTimeField(blank=True, null=True)
    # Date ribbon on the card, e.g. "JUL 04 - 07, 2026".
    date_badge = models.CharField(max_length=100, blank=True)

    # Ticketing: base price + symbol (prototype mixes $, EUR, JPY, GBP, KRW),
    # availability line, and optional external checkout link.
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency_symbol = models.CharField(max_length=4, default="$")
    status_line = models.CharField(
        max_length=200, blank=True, help_text="e.g. '4-Day Badges Available'"
    )
    ticket_link = models.URLField(blank=True)

    # Guest / guest-chip highlights, one per line in admin.
    highlights = models.TextField(
        blank=True, help_text="One guest or highlight per line."
    )

    # Visibility: only published events reach the listing.
    is_published = models.BooleanField(default=True)
    image = models.ImageField(upload_to="events/images", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ["start_datetime", "title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Default the city filter key from the display name on first save.
        if not self.city_slug and self.city:
            from django.utils.text import slugify

            self.city_slug = slugify(self.city)
        super().save(*args, **kwargs)

    # Guest chips for the card; blank lines are skipped.
    @property
    def highlight_list(self):
        return [h.strip() for h in self.highlights.splitlines() if h.strip()]

    # Display name for the stored category key.
    @property
    def category_label(self):
        return dict(self.CATEGORY_CHOICES).get(self.category, self.category)