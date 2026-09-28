from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Event


def event_list(request):
    """Conventions listing with city / category filters and search.

    Mirrors ``merch.views.merch_list``: published-only base queryset,
    GET filters, start-date ordering. The map pins and venue panel are
    fed from the same queryset so cards and map stay in sync.
    """
    # 1. Base queryset: only published events, soonest first.
    items = Event.objects.filter(is_published=True).order_by(
        "start_datetime", "title"
    )

    city = (request.GET.get("city") or "all").strip()
    category = (request.GET.get("category") or "all").strip()
    query = (request.GET.get("q") or "").strip()

    # 2. Distinct city options for the filter dropdown.
    city_options = (
        Event.objects.filter(is_published=True)
        .exclude(city_slug="")
        .values("city_slug", "city")
        .distinct()
        .order_by("city")
    )
    known_cities = {c["city_slug"] for c in city_options}

    # 3. City + category filters; unknown values fall back to "all".
    if city in known_cities:
        items = items.filter(city_slug=city)
    else:
        city = "all"
    known_categories = set(Event.objects.filter(is_published=True, category__isnull=False).values_list('category__slug', flat=True).distinct())
    if category in known_categories:
        items = items.filter(category__slug=category)
    else:
        category = "all"

    # 4. Free-text search across title, description, venue and city.
    if query:
        items = items.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(venue__icontains=query)
            | Q(city__icontains=query)
        )

    context = {
        "events": items,
        "city_options": city_options,
        "categories": [(item['category__slug'], item['category__name']) for item in Event.objects.filter(is_published=True, category__isnull=False).values('category__slug', 'category__name').distinct().order_by('category__name')],
        "selected_city": city,
        "selected_category": category,
        "query": query,
        "total_count": items.count(),
    }
    return render(request, "event-list.html", context)


def event_detail(request, pk):
    """Single convention page: schedule, venue panel, related events."""
    # Unpublished events stay hidden (404) even with a direct link.
    event = get_object_or_404(Event, pk=pk, is_published=True)

    # Up to 4 same-category events for the "More" row.
    related = (
        Event.objects.filter(category=event.category, is_published=True)
        .exclude(pk=event.pk)
        .order_by("start_datetime", "title")[:4]
    )

    context = {
        "event": event,
        "related_events": related,
    }
    return render(request, "event-detail.html", context)
