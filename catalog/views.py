from django.shortcuts import render, redirect, get_object_or_404
from django.utils.text import slugify
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, F, Q
from django.core.paginator import Paginator
from django.contrib.contenttypes.models import ContentType
from .models import Content, Category, Genre
from .forms import ContentSubmissionForm
from dashboard.models import ActivityLog, Actions


def explore(request):
    """Show public category browsing and login-gated advanced filters."""
    contents = Content.objects.filter(is_published=True).select_related('category').prefetch_related('genres').annotate(avg_rating=Avg('ratings__rating'))
    categories = Category.objects.all()
    genres = Genre.objects.all()
    category = (request.GET.get('category') or '').strip()
    if category:
        contents = contents.filter(category__slug=category)

    requested = any(request.GET.get(key) for key in ('q', 'genre', 'year', 'content_type', 'sort'))
    login_to_unlock = requested and not request.user.is_authenticated
    selected = {'q': '', 'genre': '', 'year': '', 'content_type': '', 'sort': 'latest'}
    if request.user.is_authenticated:
        selected = {key: (request.GET.get(key) or '').strip() for key in selected}
        selected['sort'] = selected['sort'] or 'latest'
        if selected['q']:
            contents = contents.filter(Q(title__icontains=selected['q']) | Q(description__icontains=selected['q']))
        if selected['genre']:
            contents = contents.filter(genres__slug=selected['genre'])
        if selected['year'].isdigit():
            contents = contents.filter(release_date__year=selected['year'])
        if selected['content_type'] in dict(Content._meta.get_field('content_type').choices):
            contents = contents.filter(content_type=selected['content_type'])
        if selected['sort'] == 'popular':
            contents = contents.order_by('-popularity_score', '-view_count', 'title')
        elif selected['sort'] == 'alpha':
            contents = contents.order_by('title')
        else:
            selected['sort'] = 'latest'
            contents = contents.order_by('-release_date', '-created_at')
    else:
        contents = contents.order_by('-release_date', '-created_at')

    paginator = Paginator(contents.distinct(), 12)
    page_obj = paginator.get_page(request.GET.get('page'))
    query_params = request.GET.copy()
    query_params.pop('page', None)

    context = {
        'contents': page_obj.object_list,
        'page_obj': page_obj,
        'query_string': query_params.urlencode(),
        'categories': categories,
        'genres': genres,
        'selected_category': category,
        'selected_filters': selected,
        'content_type_choices': Content._meta.get_field('content_type').choices,
        'login_to_unlock': login_to_unlock,
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
        form = ContentSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            base_slug = slugify(submission.title) or 'submission'
            unique_slug = base_slug
            counter = 1
            while Content.objects.filter(slug=unique_slug).exists():
                unique_slug = f'{base_slug}-{counter}'
                counter += 1
            submission.slug = unique_slug
            submission.source_type = 'embed' if submission.video_url else 'upload'
            submission.is_published = False
            submission.created_by = request.user
            submission.save()
            form.save_m2m()
            ActivityLog.objects.create(user=request.user, action=Actions.SUBMITTED, target_type='Content', target_id=submission.pk)
            messages.success(request, 'Submission received and sent for review.')
            return redirect('submit-content')
    else:
        form = ContentSubmissionForm()

    categories = Category.objects.all()
    genres = Genre.objects.all()
    user_submissions = Content.objects.filter(created_by=request.user).order_by('-created_at')

    context = {
        'categories': categories,
        'genres': genres,
        'form': form,
        'user_submissions': user_submissions,
    }
    return render(request, 'submit-content.html', context)
