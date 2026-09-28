# core/views.py
from django.http import JsonResponse
from django.shortcuts import render
from catalog.models import Category, Content
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import redirect
from accounts.forms import ProfileForm
from accounts.models import Avatar, Profile

def home(request):
    return render(request, 'home.html', {
        'categories': Category.objects.all()[:8],
        'featured_contents': Content.objects.filter(is_published=True).order_by('-popularity_score')[:8],
    })

def sitemap_view(request):
    return render(request, 'sitemap.html')

@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            saved = form.save()
            if saved.custom_avatar:
                saved.avatar = None
                saved.save(update_fields=['avatar'])
            messages.success(request, 'Your profile preferences have been saved.')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'profile.html', {
        'profile': profile, 'form': form, 'categories': Category.objects.all(),
        'avatars': Avatar.objects.filter(is_active=True),
        'selected_category_ids': set(profile.favorite_categories.values_list('pk', flat=True)),
    })

def ratelimited(request, exception=None):
    if request.path.startswith('/chatbot/'):
        return JsonResponse(
            {'answer': "You're sending messages too quickly. Please wait a moment and try again.",
             'chips': []},
            status=429,
        )
    return render(request, 'core/ratelimited.html', status=429)
