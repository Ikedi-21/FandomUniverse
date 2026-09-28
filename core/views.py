# core/views.py
from django.http import JsonResponse
from django.shortcuts import render

def ratelimited(request, exception=None):
    if request.path.startswith('/chatbot/'):
        return JsonResponse(
            {'answer': "You're sending messages too quickly. Please wait a moment and try again.",
             'chips': []},
            status=429,
        )
    return render(request, 'core/ratelimited.html', status=429)