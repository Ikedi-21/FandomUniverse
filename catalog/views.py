from django.shortcuts import render, redirect, get_object_or_404
from django.utils.text import slugify
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.contrib.contenttypes.models import ContentType
from .models import Content, Category, Genre


def explore(request):
    """Handles the catalog view, filtering published content, categories, and genres."""
    contents = Content.objects.filter(is_published=True).prefetch_related('genres', 'category')
    categories = Category.objects.all()
    genres = Genre.objects.all()

    context = {
        'contents': contents,
        'categories': categories,
        'genres': genres,
    }
    return render(request, 'explore.html', context)


def content_detail(request, slug):
    """Handles individual content viewing, loading the item and related items in the same category."""
    content = get_object_or_404(
        Content.objects.select_related('category', 'created_by'),
        slug=slug,
        is_published=True,
    )

    # Atomic view bump
    Content.objects.filter(pk=content.pk).update(view_count=F('view_count') + 1)
    content.view_count += 1

    related_contents = (
        Content.objects.filter(category=content.category, is_published=True)
        .exclude(pk=content.pk)
        .select_related('category')
        .prefetch_related('genres')[:3]
    )

    # Bookmark state for this user
    content_type = ContentType.objects.get_for_model(Content)
    is_bookmarked = False
    bookmark_note = ''

    if request.user.is_authenticated:
        from engagements.models import Bookmark
        bm = Bookmark.objects.filter(
            user=request.user,
            content_type=content_type,
            object_id=content.pk,
        ).first()
        if bm:
            is_bookmarked = True
            bookmark_note = bm.note or ''

    context = {
        'content': content,
        'related_contents': related_contents,
        'content_type_id': content_type.id,
        'is_bookmarked': is_bookmarked,
        'bookmark_note': bookmark_note,
    }
    return render(request, 'content-detail.html', context)


@login_required
def submit_content(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        category_id = request.POST.get('category')
        content_type = request.POST.get('content_type')
        video_url = request.POST.get('video_url')
        description = request.POST.get('description')
        thumbnail = request.FILES.get('thumbnail')

        category = Category.objects.get(id=category_id)

        base_slug = slugify(title)
        unique_slug = base_slug
        counter = 1
        while Content.objects.filter(slug=unique_slug).exists():
            unique_slug = f"{base_slug}-{counter}"
            counter += 1

        Content.objects.create(
            title=title,
            slug=unique_slug,
            category=category,
            content_type=content_type,
            video_url=video_url,
            description=description,
            thumbnail=thumbnail,
            is_published=False,
            created_by=request.user,
        )

        messages.success(request, 'Submission received! Your content is now in the review queue.')
        return redirect('submit-content')

    categories = Category.objects.all()
    user_submissions = Content.objects.filter(created_by=request.user).order_by('-created_at')

    context = {
        'categories': categories,
        'user_submissions': user_submissions,
    }
    return render(request, 'submit-content.html', context)