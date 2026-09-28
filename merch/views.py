from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Merch


def merch_list(request):
    """Storefront gallery.

    Mirrors ``characters.views.character_list``: category filter, text
    search, sorting, pagination. Upcoming drops are exposed separately so
    the template can render the countdown section from the DB.
    """
    # 1. Base queryset: only published items reach the storefront.
    items = Merch.objects.filter(is_published=True)

    category = request.GET.get("category") or "all"
    query = request.GET.get("q", "").strip()
    sort = request.GET.get("sort") or "featured"

    # 2. Category tabs (figures / apparel / props); unknown values fall
    # back to "all" instead of returning an empty page.
    valid_categories = dict(Merch.CATEGORY_CHOICES)
    if category in valid_categories:
        items = items.filter(category=category)
    else:
        category = "all"

    # 3. Free-text search across name, description, franchise and tags.
    if query:
        items = items.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(franchise__icontains=query)
            | Q(tags__icontains=query)
        )

    # 4. Sort options from the store controls; "featured" = most viewed.
    if sort == "price-low":
        items = items.order_by("price", "name")
    elif sort == "price-high":
        items = items.order_by("-price", "name")
    elif sort == "alpha":
        items = items.order_by("name")
    else:
        sort = "featured"
        items = items.order_by("-view_count", "name")

    # 5. Paginate the grid, 12 products per page.
    paginator = Paginator(items, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    # 6. Upcoming drops feed the countdown section independently of the
    # grid filters above.
    upcoming_drops = (
        Merch.objects.filter(is_published=True, is_upcoming=True)
        .order_by("release_date", "-view_count")[:5]
    )

    context = {
        "page_obj": page_obj,
        "products": page_obj.object_list,
        "upcoming_drops": upcoming_drops,
        "categories": Merch.CATEGORY_CHOICES,
        "selected_category": category,
        "query": query,
        "sort": sort,
        "total_count": paginator.count,
    }
    return render(request, "merch-list.html", context)


def merch_detail(request, pk):
    """Single product page with view-count tracking and related items."""
    # Unpublished products stay hidden (404) even with a direct link.
    product = get_object_or_404(Merch, pk=pk, is_published=True)

    # Track detail views; single UPDATE avoids a read-modify-write race.
    Merch.objects.filter(pk=product.pk).update(view_count=product.view_count + 1)
    product.refresh_from_db(fields=["view_count"])

    # Up to 4 same-category items for the "More" row on the detail page.
    related = (
        Merch.objects.filter(
            category=product.category, is_published=True
        )
        .exclude(pk=product.pk)
        .order_by("-view_count")[:4]
    )

    context = {
        "product": product,
        "related_products": related,
    }
    return render(request, "merch-detail.html", context)
