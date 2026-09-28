from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.contenttypes.models import ContentType
from .models import Feedback, Bookmark
from dashboard.models import ActivityLog, Actions


@login_required
def feedback_view(request):
    """Show the feedback form and handle submissions."""

    if request.method == 'POST':
        fb_type = request.POST.get('type', 'bug')
        severity = request.POST.get('severity', 'low')
        subject = (request.POST.get('subject') or '').strip()
        message_text = (request.POST.get('message') or '').strip()

        errors = []
        if not subject:
            errors.append('Subject is required.')
        if not message_text:
            errors.append('Message is required.')
        if fb_type not in dict(Feedback.TYPE_CHOICES):
            errors.append('Invalid feedback type.')
        if severity not in dict(Feedback.SEVERITY_CHOICES):
            errors.append('Invalid severity.')

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, 'feedback.html', {
                'user_submissions': Feedback.objects.filter(user=request.user),
                'form_data': request.POST,
            })

        feedback = Feedback.objects.create(
            user=request.user,
            type=fb_type,
            severity=severity,
            subject=subject,
            message=message_text,
        )
        ActivityLog.objects.create(user=request.user, action=Actions.FEEDBACK, target_type='Feedback', target_id=feedback.pk)
        messages.success(request, 'Ticket logged. Our team will review it within 24–48 hours.')
        return redirect('feedback')

    return render(request, 'feedback.html', {
        'user_submissions': Feedback.objects.filter(user=request.user)[:10],
    })


@login_required
@require_POST
def bookmark_toggle(request):
    """POST endpoint: create / delete / update a Bookmark."""
    content_type_id = request.POST.get('content_type_id')
    object_id = request.POST.get('object_id')
    note = (request.POST.get('note') or '').strip()

    if not content_type_id or not object_id:
        return JsonResponse({'ok': False, 'error': 'Missing fields'}, status=400)

    try:
        ct = ContentType.objects.get(pk=content_type_id)
    except ContentType.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Invalid content type'}, status=400)

    bm, created = Bookmark.objects.get_or_create(
        user=request.user,
        content_type=ct,
        object_id=object_id,
        defaults={'note': note},
    )
    if created:
        ActivityLog.objects.create(user=request.user, action=Actions.BOOKMARKED, target_type=ct.model, target_id=object_id)

    # Existing bookmark + note provided → update note, don't delete
    if not created and note:
        bm.note = note
        bm.save(update_fields=['note'])
        return JsonResponse({'ok': True, 'bookmarked': True, 'updated_note': True})

    # Existing bookmark, no note → delete (toggle off)
    if not created:
        bm.delete()
        return JsonResponse({'ok': True, 'bookmarked': False})

    # Newly created
    return JsonResponse({'ok': True, 'bookmarked': True, 'created': True})


@login_required
def bookmark_list(request):
    """Page listing all the user's bookmarks."""
    bookmarks = Bookmark.objects.filter(user=request.user).select_related('content_type')
    return render(request, 'bookmark-list.html', {'bookmarks': bookmarks})
