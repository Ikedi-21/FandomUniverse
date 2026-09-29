import os
import re
from pathlib import Path
from django.contrib.auth import get_user_model
from django.contrib.staticfiles import finders
from django.test import Client, TestCase
from django.urls import reverse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FandomUniverse.settings')

class TemplateWiringTests(TestCase):
    def test_project_template_urls_reverse_and_static_files_exist(self):
        roots = [Path(app) / 'templates' for app in (
            'accounts', 'article', 'catalog', 'characters', 'chatbot', 'core',
            'dashboard', 'engagements', 'events', 'media_centre', 'merch'
        )]
        detail_args = {
            'content-detail': ['sample'],
            'article-detail': ['sample'],
            'character-detail': [1],
            'event-detail': [1],
            'merch-detail': [1],
            'accounts:password_reset_confirm': None,
        }
        reset_kwargs = {'uidb64': 'MQ', 'token': 'token'}
        failures = []
        for root in roots:
            if not root.exists():
                continue
            for path in root.rglob('*.html'):
                text = path.read_text(encoding='utf-8', errors='ignore')
                for match in re.finditer(r"\{%\s*url\s+([^%]+)%\}", text):
                    name = match.group(1).strip().split()[0].strip("'\"")
                    try:
                        if name == 'accounts:password_reset_confirm':
                            reverse(name, kwargs=reset_kwargs)
                        elif name in detail_args and detail_args[name] is not None:
                            reverse(name, args=detail_args[name])
                        elif name in detail_args:
                            reverse(name)
                        else:
                            reverse(name)
                    except Exception as exc:
                        failures.append(f'{path}: {name}: {exc}')
                for asset in re.findall(r"\{%\s*static\s+([^%]+)%\}", text):
                    asset = asset.strip().split()[0].strip("'\"")
                    if not finders.find(asset):
                        failures.append(f'{path}: missing static {asset}')
        self.assertEqual(failures, [])

class RouteAccessTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='test-member', email='member@example.test', password='MemberPassword!2026', email_verified=True)
        self.staff = User.objects.create_user(username='test-staff', email='staff@example.test', password='StaffPassword!2026', is_staff=True, is_superuser=True, email_verified=True)

    def test_public_routes_render(self):
        client = Client(SERVER_NAME='127.0.0.1')
        for path in ('/', '/catalog/explore/', '/article/', '/articles/', '/media-centre/', '/events/', '/characters/', '/merch/', '/sitemap/', '/accounts/login/', '/accounts/register/', '/accounts/password-reset/'):
            with self.subTest(path=path):
                self.assertEqual(client.get(path).status_code, 200)

    def test_protected_routes_redirect_anonymous(self):
        client = Client(SERVER_NAME='127.0.0.1')
        for path in ('/profile/', '/dashboard/', '/bookmarks/', '/catalog/submit-content/'):
            with self.subTest(path=path):
                self.assertEqual(client.get(path).status_code, 302)

    def test_custom_admin_pages_require_staff(self):
        client = Client(SERVER_NAME='127.0.0.1')
        for path in ('/dashboard/admin/', '/dashboard/admin/submissions/', '/dashboard/admin/chatbot-faq/', '/dashboard/admin/content-form/'):
            with self.subTest(path=path):
                self.assertEqual(client.get(path).status_code, 302)
        client.force_login(self.staff)
        self.assertEqual(client.get('/dashboard/admin/').status_code, 200)
        client.force_login(self.user)
        self.assertEqual(client.get('/dashboard/admin/').status_code, 302)

    def test_profile_saves_current_preferences(self):
        from accounts.models import Profile
        from catalog.models import Category
        category = Category.objects.create(name='Test fandom', slug='test-fandom')
        client = Client(SERVER_NAME='127.0.0.1')
        client.force_login(self.user)
        response = client.post('/profile/', {
            'bio': 'A short test bio', 'theme': 'dark', 'font_size': 'large',
            'favorite_categories': [category.pk], 'avatar': '',
        })
        self.assertEqual(response.status_code, 302)
        profile = Profile.objects.get(user=self.user)
        self.assertEqual(profile.theme, 'dark')
        self.assertEqual(profile.font_size, 'large')
        self.assertEqual(list(profile.favorite_categories.all()), [category])

    def test_content_submission_uses_one_pending_flow(self):
        from catalog.models import Category, Content
        category = Category.objects.create(name='Submission fandom', slug='submission-fandom')
        client = Client(SERVER_NAME='127.0.0.1')
        client.force_login(self.user)
        response = client.post('/catalog/submit-content/', {
            'title': 'A valid community article', 'category': category.pk,
            'content_type': 'article', 'description': 'An article description',
            'body': 'The article body.',
        })
        self.assertEqual(response.status_code, 302)
        item = Content.objects.get(title='A valid community article')
        self.assertFalse(item.is_published)
        self.assertEqual(item.created_by, self.user)

    def test_bookmark_toggle_and_rating_update(self):
        from catalog.models import Category, Content
        from engagements.models import Bookmark
        from media_centre.models import Rating
        from django.contrib.contenttypes.models import ContentType
        category = Category.objects.create(name='Engagement fandom', slug='engagement-fandom')
        item = Content.objects.create(title='Engagement item', slug='engagement-item', category=category, is_published=True)
        client = Client(SERVER_NAME='127.0.0.1')
        client.force_login(self.user)
        bookmark_response = client.post('/engagements/bookmarks/toggle/', {
            'content_type_id': ContentType.objects.get_for_model(Content).pk,
            'object_id': item.pk,
        })
        self.assertEqual(bookmark_response.status_code, 200)
        self.assertEqual(Bookmark.objects.filter(user=self.user, object_id=item.pk).count(), 1)
        for score in ('4', '5'):
            response = client.post('/media_centre/rate/', {'content': item.slug, 'rating': score})
            self.assertEqual(response.status_code, 200)
        self.assertEqual(Rating.objects.filter(user=self.user, media=item).count(), 1)

    def test_verification_link_activates_user(self):
        from django.utils.encoding import force_bytes
        from django.utils.http import urlsafe_base64_encode
        from accounts.tokens import email_token_generator
        self.user.email_verified = False
        self.user.save(update_fields=['email_verified'])
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = email_token_generator.make_token(self.user)
        client = Client(SERVER_NAME='127.0.0.1')
        response = client.get(f'/accounts/verify/{uid}/{token}/')
        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.email_verified)
