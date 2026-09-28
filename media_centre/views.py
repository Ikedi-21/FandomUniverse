from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST

from catalog.models import Content

from .models import Rating
from dashboard.models import ActivityLog, Actions

def media_list(request):
    items = Content.objects.filter(is_published=True, content_type__in=['video', 'audio']).prefetch_related('tags').order_by('-popularity_score')
    return render(request, 'media-list.html', {'items': items})


@login_required
@require_POST
def submit_rating(request):
    """Persist a 1-5 star rating for a catalog item. JSON only.

    Fetch contract (for the content-detail star widget):
        POST /media_centre/rate/
        Headers: X-CSRFToken (from the csrftoken cookie)
        Body (form-encoded): content=<content slug>&rating=<1-5>

    Responses:
        200 {"ok": true, "rating": int, "average_rating": float,
             "rating_count": int, "created": bool}
        400 {"ok": false, "error": ...}   (bad/missing score or slug)
        404 {"ok": false, "error": ...}   (unknown or unpublished content)
        405 for non-POST; anonymous users are redirected to login.
    Re-rating overwrites the user's existing row (see Rating.Meta).
    """
    slug = (request.POST.get("content") or "").strip()
    raw_score = (request.POST.get("rating") or "").strip()

    # 1. Validate the score is an integer in range.
    try:
        score = int(raw_score)
    except (TypeError, ValueError):
        return JsonResponse(
            {"ok": False, "error": "Rating must be an integer."}, status=400
        )
    if not 1 <= score <= 5:
        return JsonResponse(
            {"ok": False, "error": "Rating must be between 1 and 5."},
            status=400,
        )

    # 2. Published content only; unknown slugs 404.
    if not slug:
        return JsonResponse(
            {"ok": False, "error": "Missing content slug."}, status=400
        )
    content = get_object_or_404(Content, slug=slug, is_published=True)

    # 3. One row per user per item; re-rating updates it.
    _, created = Rating.objects.update_or_create(
        user=request.user,
        media=content,
        defaults={"rating": score},
    )
    ActivityLog.objects.create(user=request.user, action=Actions.RATED, target_type='Content', target_id=content.pk)

    # 4. Recompute the displayed average from all ratings.
    aggregate = Rating.objects.filter(media=content).aggregate(
        avg=Avg("rating")
    )
    average_rating = round(aggregate["avg"] or 0.0, 1)
    count = Rating.objects.filter(media=content).count()

    return JsonResponse(
        {
            "ok": True,
            "rating": score,
            "average_rating": average_rating,
            "rating_count": count,
            "created": created,
        }
    )
