from django.shortcuts import render, redirect, get_object_or_404
from django.utils.text import slugify
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Content, Category, Genre



# Create your views here.

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
    # Find the specific content item by its slug
    content = get_object_or_404(Content, slug=slug, is_published=True)
    
    # Increment view count each time the page is opened
    content.view_count += 1
    content.save(update_fields=['view_count'])
    
    # Fetch up to 3 other published items in the same category for the "Related Content" row
    related_contents = Content.objects.filter(
        category=content.category,
        is_published=True
    ).exclude(pk=content.pk)[:3]
    
    context = {
        'content': content,
        'related_contents': related_contents,
    }
    return render(request, 'content-detail.html', context)

@login_required
def submit_content(request):
    # 1. Handle Form Submission (POST)
    if request.method == 'POST':
        title = request.POST.get('title')
        category_id = request.POST.get('category')
        content_type = request.POST.get('content_type')
        video_url = request.POST.get('video_url')
        description = request.POST.get('description')
        
        # Files are stored in request.FILES
        thumbnail = request.FILES.get('thumbnail')

        # Fetch the selected Category instance
        category = Category.objects.get(id=category_id)
        
        # Auto-generate a unique URL slug
        base_slug = slugify(title)
        unique_slug = base_slug
        counter = 1
        while Content.objects.filter(slug=unique_slug).exists():
            unique_slug = f"{base_slug}-{counter}"
            counter += 1

        # Save to database
        new_content = Content.objects.create(
            title=title,
            slug=unique_slug,
            category=category,
            content_type=content_type,
            video_url=video_url,
            description=description,
            thumbnail=thumbnail,
            is_published=False,  # Pending review state
            created_by=request.user,  # Attach current logged-in user
        )
        
        messages.success(request, 'Submission received! Your content is now in the review queue.')
        return redirect('submit-content')

    # 2. Handle Page Load (GET)
    categories = Category.objects.all()
    
    # Fetch this specific user's previous submissions
    user_submissions = Content.objects.filter(created_by=request.user).order_by('-created_at')

    context = {
        'categories': categories,
        'user_submissions': user_submissions,
    }
    
    # Make sure this matches your exact HTML file name in your templates folder
    return render(request, 'submit-content.html', context)


