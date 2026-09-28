from django.shortcuts import render

# Create your views here.
from django.shortcuts import get_object_or_404, render
from catalog.models import Content

def article_list(request):
    articles = Content.objects.filter(is_published=True, content_type='article').select_related('category').order_by('-release_date', '-created_at')
    return render(request, 'article-list.html', {'articles': articles})

def article_detail(request, slug):
    article = get_object_or_404(Content, slug=slug, content_type='article', is_published=True)
    return render(request, 'content-detail.html', {'content': article})
