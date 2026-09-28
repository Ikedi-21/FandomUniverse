from django.db import models


class Merch(models.Model):
    """Store item for the Merch & Official Goodies Store.

    Source design: ``characters/templates/merch-list.html`` (product cards
    grouped by figures / apparel / props) and
    ``characters/templates/merch-detail.html`` (gallery + purchase panel).
    """

    CATEGORY_CHOICES = [
        ("figures", "Statues & Figures"),
        ("apparel", "Streetwear & Apparel"),
        ("props", "Prop Replicas"),
    ]

    # Identity: name, franchise line (e.g. "Solo Leveling"), size line
    # (e.g. "1/7 Scale"), free-form tags, and store category driving the
    # figures / apparel / props filter tabs.
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    franchise = models.CharField(max_length=200, blank=True)
    sub_label = models.CharField(max_length=200, blank=True)
    tags = models.CharField(max_length=200, blank=True)
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, default="figures"
    )
    # Small ribbon shown on the card, e.g. "Limited Edition", "Bestseller".
    badge = models.CharField(max_length=100, blank=True)

    # Pricing and availability. stock=0 means pre-order / sold out
    # (see stock_label below).
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    stock = models.PositiveIntegerField(default=0)

    # Visibility: published items appear in the store; upcoming items also
    # feed the "Limited Batch Drops" countdown section via release_date.
    is_upcoming = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    release_date = models.DateTimeField(blank=True, null=True)
    view_count = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to="merch/images", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    # Human-readable availability badge used by both merch templates.
    @property
    def stock_label(self):
        if self.is_upcoming:
            return "Pre-Order"
        if self.stock <= 0:
            return "Sold Out"
        if self.stock <= 5:
            return f"In Stock ({self.stock} left)"
        return "In Stock"

    # Display name for the stored category key ("figures" -> label).
    @property
    def category_label(self):
        return dict(self.CATEGORY_CHOICES).get(self.category, self.category)