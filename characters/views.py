from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from catalog.models import Category
from .models import CharacterProfile


def character_list(request):
    characters = CharacterProfile.objects.filter(
        is_published=True
    ).select_related("category")

    category_slug = request.GET.get("category")
    query = request.GET.get("q")

    if category_slug:
        characters = characters.filter(category__slug=category_slug)

    if query:
        characters = characters.filter(name__icontains=query)

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
    character = get_object_or_404(
        CharacterProfile.objects.select_related("category"),
        pk=pk,
        is_published=True,
    )
    related_characters = CharacterProfile.objects.filter(
        category=character.category, is_published=True
    ).exclude(pk=character.pk)[:4]

    context = {
        "character": character,
        "related_characters": related_characters,
    }
    return render(request, "character-detail.html", context)