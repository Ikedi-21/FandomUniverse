from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
# NOTE: Category must come from .models (local). Importing catalog's
# Category here used to break the ?category=<slug> filter with a FieldError.
from .models import Category, CharacterProfile


def character_list(request):
    """Character archive grid with fandom filter, name search, pagination."""
    # Only published dossiers, category prefetched for the card badges.
    characters = CharacterProfile.objects.filter(
        is_published=True
    ).select_related("category")

    category_slug = request.GET.get("category") or ""
    category_slug = category_slug.strip()
    query = (request.GET.get("q") or "").strip()

    # Fandom filter (?category=<slug>); blank means "All fandoms".
    if category_slug:
        characters = characters.filter(category__slug=category_slug)

    # Name search (?q=...).
    if query:
        characters = characters.filter(name__icontains=query)

    # 12 cards per page, alphabetical.
    paginator = Paginator(characters.order_by("name"), 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "page_obj": page_obj,
        "characters": page_obj.object_list,
        "categories": Category.objects.all(),
        "selected_category": category_slug,
        "query": query or "",
    }
    return render(request, "character-list.html", context)


def character_detail(request, pk):
    """Single dossier: hero, bio, plus up to 4 same-fandom characters."""
    character = get_object_or_404(
        CharacterProfile.objects.select_related("category"),
        pk=pk,
        is_published=True,
    )
    # Same fandom, excluding the current character.
    related_characters = CharacterProfile.objects.filter(
        category=character.category, is_published=True
    ).exclude(pk=character.pk)[:4]

    context = {
        "character": character,
        "related_characters": related_characters,
    }
    return render(request, "character-detail.html", context)