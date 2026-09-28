import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import ChatbotQuery
from .services import get_response
from django_ratelimit.decorators import ratelimit

MAX_LEN = 255          # matches ChatbotQuery.message


@require_POST
def ask(request):
    try:
        message = json.loads(request.body).get('message', '')
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    message = str(message).strip()[:MAX_LEN]
    if not message:
        return JsonResponse({'error': 'Message is required'}, status=400)

    if not request.session.session_key:
        request.session.create()

    result = get_response(message)
    ChatbotQuery.objects.create(
        user=request.user if request.user.is_authenticated else None,
        session_key=request.session.session_key,
        message=message,
        response=result['answer'],
        matched_faq=result['faq'],
    )
    return JsonResponse({'answer': result['answer'], 'chips': result['chips']})



# @require_POST
# @ratelimit(key='ip', rate='20/m')
# def ask(request):
