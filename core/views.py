# core/views.py
from django.http import JsonResponse
from django.shortcuts import render
from catalog.models import Category, Content
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'home.html', {
        'categories': Category.objects.all()[:8],
        'featured_contents': Content.objects.filter(is_published=True).order_by('-popularity_score')[:8],
    })

def sitemap_view(request):
    return render(request, 'sitemap.html')

@login_required
def profile_view(request):
    return render(request, 'profile.html', {'profile': getattr(request.user, 'profile', None), 'categories': Category.objects.all()})

def ratelimited(request, exception=None):
    if request.path.startswith('/chatbot/'):
        return JsonResponse(
            {'answer': "You're sending messages too quickly. Please wait a moment and try again.",
             'chips': []},
            status=429,
        )
    return render(request, 'core/ratelimited.html', status=429)
