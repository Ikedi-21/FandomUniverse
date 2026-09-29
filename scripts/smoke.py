"""Small role-based HTTP smoke check; safe to run repeatedly."""
import django
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FandomUniverse.settings')
django.setup()
from django.contrib.auth import get_user_model
from django.test import Client
from catalog.models import Content
from characters.models import CharacterProfile
from events.models import Event
from merch.models import Merch

User = get_user_model()
normal, _ = User.objects.get_or_create(username='demo_user', defaults={'email': 'demo@fanhubplus.local'})
normal.email_verified = True
normal.save()
staff, _ = User.objects.get_or_create(username='admin', defaults={'email': 'admin@fanhubplus.local'})
staff.is_staff = True
staff.is_superuser = True
staff.email_verified = True
staff.save()
content = Content.objects.filter(is_published=True).first()
character = CharacterProfile.objects.filter(is_published=True).first()
product = Merch.objects.filter(is_published=True).first()
event = Event.objects.filter(is_published=True).first()
detail_content = f'/catalog/content/{content.slug}/' if content else '/catalog/content/missing/'
detail_character = f'/characters/{character.pk}/' if character else '/characters/0/'
detail_merch = f'/merch/{product.pk}/' if product else '/merch/0/'
detail_event = f'/events/{event.pk}/' if event else '/events/0/'
urls = [
    '/', '/admin/', '/catalog/explore/', detail_content,
    '/catalog/submit-content/', '/characters/', detail_character,
    '/merch/', detail_merch, '/events/', detail_event, '/article/', '/articles/',
    '/media-centre/', '/accounts/login/', '/accounts/register/',
    '/accounts/verify/sent/', '/accounts/verify/resend/',
    '/accounts/password-reset/', '/profile/', '/dashboard/', '/dashboard/admin/',
    '/dashboard/admin/submissions/', '/dashboard/admin/chatbot-faq/',
    '/dashboard/admin/content-form/', '/bookmarks/', '/engagements/',
    '/sitemap/', '/not-a-real-url/',
]
clients = {
    'anon': Client(SERVER_NAME='127.0.0.1'),
    'user': Client(SERVER_NAME='127.0.0.1'),
    'staff': Client(SERVER_NAME='127.0.0.1'),
}
clients['user'].force_login(normal)
clients['staff'].force_login(staff)
print(f'{"URL":48} {"anon":6} {"user":6} {"staff":6} error')
for url in urls:
    results = []
    for client in clients.values():
        try:
            response = client.get(url)
            results.append((response.status_code, ''))
        except Exception as exc:
            results.append((500, f'{type(exc).__name__}: {exc}'))
    error = next((message for _, message in results if message), '')
    print(f'{url:48} {results[0][0]:6} {results[1][0]:6} {results[2][0]:6} {error}')
