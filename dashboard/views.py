from datetime import timedelta
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from engagements.models import Bookmark
from catalog.models import Content
from dashboard.models import ActivityLog, Actions
from characters.models import CharacterProfile
from merch.models import Merch
from accounts.models import Profile
from article.models import ApprovalStatus, FanSubmission
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_POST
from chatbot.models import ChatbotFAQ
from catalog.models import Category
from catalog.models import Content
from django.utils.text import slugify
from .forms import StaffContentForm
from django.contrib.auth import get_user_model
from django.db.models import Count
from chatbot.models import ChatbotQuery
from engagements.models import Feedback

# Create your views here.


from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def admin_overview(request):
    User = get_user_model()
    month_ago = timezone.now() - timedelta(days=30)
    pending_count = FanSubmission.objects.filter(status=ApprovalStatus.PENDING).count()
    return render(request, "admin-overview.html", {
        'active_users': User.objects.filter(is_active=True, last_login__gte=month_ago).count(),
        'published_count': Content.objects.filter(is_published=True).count(),
        'pending_count': pending_count,
        'chatbot_query_count': ChatbotQuery.objects.count(),
        'open_feedback_count': Feedback.objects.exclude(status='resolved').count(),
        'category_counts': Category.objects.annotate(content_count=Count('contents')).order_by('-content_count', 'name'),
        'top_content': Content.objects.filter(is_published=True).select_related('category').order_by('-view_count', 'title')[:5],
        'top_merch': Merch.objects.filter(is_published=True).order_by('-view_count', 'name')[:5],
    })

@staff_member_required
def admin_submisions_queue_view(request):
    if request.method == 'POST':
        submission = FanSubmission.objects.filter(pk=request.POST.get('submission_id')).first()
        action = request.POST.get('action')
        if submission and action in {'approve', 'reject'}:
            submission.status = ApprovalStatus.APPROVED if action == 'approve' else ApprovalStatus.REJECTED
            submission.reviewed_by = request.user
            submission.reviewed_at = timezone.localdate()
            submission.review_note = (request.POST.get('review_note') or '').strip()
            submission.save(update_fields=['status', 'reviewed_by', 'reviewed_at', 'review_note'])
            ActivityLog.objects.create(user=request.user, action=Actions.SUBMITTED, target_type=f'submission_{submission.status.lower()}', target_id=str(submission.pk))
            messages.success(request, f'Submission {submission.get_status_display().lower()}.')
        else:
            messages.error(request, 'Choose a valid submission and review action.')
        return redirect('admin_submissions')
    submissions = FanSubmission.objects.select_related('user', 'category').order_by('status', '-created_at')
    return render(request, "admin-submissions-queue.html", {'submissions': submissions, 'pending_count': submissions.filter(status=ApprovalStatus.PENDING).count()})
  
@staff_member_required
def admin_chatbot_faq_view(request):
    faq_id = request.GET.get('edit') or request.POST.get('faq_id')
    faq = ChatbotFAQ.objects.filter(pk=faq_id).first() if faq_id else None
    if request.method == 'POST':
        if request.POST.get('action') == 'delete' and faq:
            faq.delete()
            messages.success(request, 'FAQ rule deleted.')
            return redirect('admin_chatbot_faq')
        question = (request.POST.get('question') or '').strip()
        keyword = (request.POST.get('keyword') or '').strip()
        answer = (request.POST.get('answer') or '').strip()
        category = Category.objects.filter(pk=request.POST.get('category')).first()
        if question and keyword and answer:
            faq = faq or ChatbotFAQ()
            faq.question, faq.keyword, faq.answer = question, keyword, answer
            faq.category = category
            faq.is_active = request.POST.get('is_active') == 'on'
            faq.save()
            messages.success(request, 'FAQ rule saved.')
            return redirect('admin_chatbot_faq')
        messages.error(request, 'Question, keywords, and answer are required.')
    return render(request, "admin-chatbot-faq.html", {'faqs': ChatbotFAQ.objects.select_related('category').order_by('question'), 'faq': faq, 'categories': Category.objects.order_by('name')})

@staff_member_required
def admin_content_form_view(request):
    item = Content.objects.filter(pk=request.GET.get('edit') or request.POST.get('content_id')).first() if (request.GET.get('edit') or request.POST.get('content_id')) else None
    if request.method == 'POST':
        form = StaffContentForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            item = form.save(commit=False)
            base = slugify(item.title) or 'content'
            candidate, suffix = base, 1
            while Content.objects.filter(slug=candidate).exclude(pk=item.pk).exists():
                candidate = f'{base}-{suffix}'
                suffix += 1
            item.slug = candidate
            item.created_by = item.created_by or request.user
            item.source_type = 'embed' if item.video_url else 'upload'
            item.save()
            form.save_m2m()
            messages.success(request, 'Content saved.')
            return redirect('admin_content_form')
    else:
        form = StaffContentForm(instance=item, initial={'is_published': True})
    return render(request, "admin-content-form.html", {'form': form, 'content': item, 'content_items': Content.objects.select_related('category').order_by('-created_at')[:30]})


@login_required
def user_dashboard_view(request):
  try:
    profile = request.user.profile
  except Profile.DoesNotExist:
    profile = None
  bookmarks = []
  for bookmark in Bookmark.objects.filter(user=request.user).select_related('content_type'):
    target = bookmark.target
    if target is None:
      continue
    model = bookmark.content_type.model_class()
    if isinstance(target, Content):
      url = f'/catalog/content/{target.slug}/'
      title = target.title
      image = target.thumbnail.url if target.thumbnail else ''
    elif isinstance(target, CharacterProfile):
      url = f'/characters/{target.pk}/'
      title = target.name
      image = target.image.url if target.image else ''
    elif isinstance(target, Merch):
      url = f'/merch/{target.pk}/'
      title = target.name
      image = target.image.url if target.image else ''
    else:
      url = ''
      title = str(target)
      image = ''
    bookmarks.append({'title': title, 'url': url, 'image': image, 'note': bookmark.note, 'type': model._meta.verbose_name.title()})
  favorite_categories = profile.favorite_categories.all() if profile else []
  return render(request, 'dashboard.html', {
    'profile': profile,
    'bookmarks': bookmarks,
    'bookmark_count': len(bookmarks),
    'favorite_categories': favorite_categories,
    'favorite_count': len(favorite_categories),
    'submission_count': Content.objects.filter(created_by=request.user, is_published=False).count(),
    'recent_activity': ActivityLog.objects.filter(user=request.user).order_by('-created_at')[:8],
  })
