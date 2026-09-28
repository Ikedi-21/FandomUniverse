from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from engagements.models import Bookmark
from catalog.models import Content
from dashboard.models import ActivityLog
from characters.models import CharacterProfile
from merch.models import Merch
from accounts.models import Profile

# Create your views here.


@user_passes_test(lambda user: user.is_staff)
def admin_overview(request):
 


  return render(request, "admin-overview.html")

@user_passes_test(lambda user: user.is_staff)
def admin_submisions_queue_view(request):
 
  
  return render(request, "admin-submissions-queue.html")
  
@user_passes_test(lambda user: user.is_staff)
def admin_chatbot_faq_view(request):
 

  return render(request, "admin-chatbot-faq.html")

@user_passes_test(lambda user: user.is_staff)
def admin_content_form_view(request):
 

  return render(request, "admin-content-form.html")


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
