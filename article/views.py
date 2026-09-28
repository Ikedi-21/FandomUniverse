from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.html import linebreaks
from django.views.decorators.http import require_POST
from django_ratelimit.decorators import ratelimit

from catalog.models import Category, Content
from .forms import FanSubmissionForm, HighlightForm
from .models import EventHighlight, FanSubmission, ApprovalStatus
from .permissions import admin_required


# ---------- public ----------
def article_list(request):
    qs = Content.objects.filter(content_type='article', is_published=True).select_related('category')
    slug = request.GET.get('category', '')
    q = request.GET.get('q', '').strip()
    if slug:
        qs = qs.filter(category__slug=slug)
    if q:
        qs = qs.filter(title__icontains=q)
    page = Paginator(qs.order_by('-release_date', '-created_at'), 9).get_page(request.GET.get('page'))
    return render(request, 'article/article_list.html', {
        'page_obj': page, 'categories': Category.objects.all(), 'active_category': slug, 'q': q,
    })


def article_detail(request, slug):
    article = get_object_or_404(Content, slug=slug, content_type='article', is_published=True)
    Content.objects.filter(pk=article.pk).update(view_count=F('view_count') + 1)
    related = (Content.objects.filter(content_type='article', is_published=True, category=article.category)
               .exclude(pk=article.pk)[:3])
    return render(request, 'article/article_detail.html', {'article': article, 'related': related})


def highlight_list(request):
    qs = EventHighlight.objects.select_related('category').order_by('display_order', 'event_date')
    slug = request.GET.get('category', '')
    if slug:
        qs = qs.filter(category__slug=slug)
    return render(request, 'article/highlight_list.html', {
        'highlights': qs, 'categories': Category.objects.all(), 'active_category': slug,
    })


# ---------- fan submissions (logged-in users) ----------
@login_required
@ratelimit(key='user', rate='5/h', method='POST')
def submit_content(request):
    form = FanSubmissionForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        submission = form.save(commit=False)
        submission.user = request.user
        submission.status = ApprovalStatus.PENDING
        submission.save()
        messages.success(request, 'Thanks! Your submission is pending admin review.')
        return redirect('article:my_submissions')
    return render(request, 'article/submit_content.html', {'form': form})


@login_required
def my_submissions(request):
    subs = FanSubmission.objects.filter(user=request.user).select_related('category').order_by('-created_at')
    return render(request, 'article/my_submissions.html', {'submissions': subs})


# ---------- admin: moderation ----------
@admin_required
def submissions_queue(request):
    pending = FanSubmission.objects.filter(status=ApprovalStatus.PENDING).select_related('user', 'category').order_by('created_at')
    selected = None
    sel_id = request.GET.get('id', '')
    if sel_id.isdigit():
        selected = pending.filter(pk=sel_id).first()
    if selected is None:
        selected = pending.first()
    recent = (FanSubmission.objects.exclude(status=ApprovalStatus.PENDING)
              .select_related('user', 'category').order_by('-reviewed_at')[:10])
    return render(request, 'article/admin/submissions_queue.html', {
        'pending': pending, 'selected': selected, 'recent': recent,
    })


@admin_required
@require_POST
def approve_submission(request, pk):
    sub = get_object_or_404(FanSubmission, pk=pk, status=ApprovalStatus.PENDING)     # a second click gives a 404, not a duplicate
    with transaction.atomic():
        Content.objects.create(
            category=sub.category,
            title=sub.title,
            content_type='article',
            body=linebreaks(sub.body, autoescape=True),                   # escape user text before it becomes HTML
            thumbnail=sub.image,
            created_by=sub.user,
            is_published=True,
        )
        sub.status = ApprovalStatus.APPROVED
        sub.review_note = request.POST.get('review_note', '').strip()
        sub.reviewed_by = request.user
        sub.reviewed_at = timezone.now()
        sub.save()
    messages.success(request, f'"{sub.title}" approved and published.')
    return redirect('article:submissions_queue')


@admin_required
@require_POST
def reject_submission(request, pk):
    sub = get_object_or_404(FanSubmission, pk=pk, status=ApprovalStatus.PENDING)
    sub.status = ApprovalStatus.REJECTED
    sub.review_note = request.POST.get('review_note', '').strip()
    sub.reviewed_by = request.user
    sub.reviewed_at = timezone.now()
    sub.save()
    messages.success(request, f'"{sub.title}" rejected.')
    return redirect('article:submissions_queue')


# ---------- admin: event highlights ----------
@admin_required
def highlight_manage(request):
    items = EventHighlight.objects.select_related('category').order_by('display_order', 'event_date')
    return render(request, 'article/admin/highlight_list.html', {'highlights': items})


@admin_required
def highlight_form(request, pk=None):
    obj = get_object_or_404(EventHighlight, pk=pk) if pk else None
    form = HighlightForm(request.POST or None, request.FILES or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Highlight saved.')
        return redirect('article:highlight_manage')
    return render(request, 'article/admin/highlight_form.html', {'form': form, 'highlight': obj})


@admin_required
@require_POST
def highlight_delete(request, pk):
    get_object_or_404(EventHighlight, pk=pk).delete()
    messages.success(request, 'Highlight deleted.')
    return redirect('article:highlight_manage')