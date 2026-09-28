from datetime import date, timedelta
from pathlib import Path
import shutil
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
from accounts.models import Profile
from article.models import ApprovalStatus, EventHighlight, FanSubmission
from catalog.models import Category, Content, Genre, Tag
from characters.models import Category as CharacterCategory, CharacterProfile
from chatbot.models import ChatbotFAQ
from engagements.models import Bookmark, Feedback
from events.models import Event
from media_centre.models import Rating
from merch.models import Merch, MerchTag

class Command(BaseCommand):
    help = 'Create repeatable fictional demo data for Fan Hub Plus.'
    passwords = {'admin': 'FandomAdmin!2026', 'demo_user': 'FandomDemo!2026', 'new_user': 'FandomNew!2026'}
    categories = ['Anime', 'Comics', 'Cosplay', 'Gaming', 'K-Pop', 'Manga', 'Movies', 'TV Shows']

    def handle(self, *args, **options):
        User = get_user_model()
        users = {}
        for name, email in [('admin', 'admin@fanhubplus.local'), ('demo_user', 'demo@fanhubplus.local'), ('new_user', 'new@fanhubplus.local')]:
            user, _ = User.objects.get_or_create(username=name, defaults={'email': email})
            user.email = email
            user.email_verified = name != 'new_user'
            user.is_staff = name == 'admin'
            user.is_superuser = name == 'admin'
            user.set_password(self.passwords[name])
            user.save()
            Profile.objects.get_or_create(user=user)
            users[name] = user

        categories = {}
        for name in self.categories:
            slug = slugify(name)
            category, _ = Category.objects.get_or_create(slug=slug, defaults={'name': name, 'description': f'Original stories and community picks in {name}.'})
            category.name = name
            category.save()
            categories[name] = category

        character_categories = {}
        for name in self.categories:
            character_categories[name] = CharacterCategory.objects.get_or_create(
                slug=slugify(name), defaults={'name': name}
            )[0]
        demo_profile = Profile.objects.get(user=users['demo_user'])
        demo_profile.favorite_categories.set(categories.values())

        genres = [Genre.objects.get_or_create(slug=slugify(name), defaults={'name': name})[0] for name in ['Adventure', 'Mystery', 'Comedy']]
        tags = [Tag.objects.get_or_create(slug=slugify(name), defaults={'name': name})[0] for name in ['Featured', 'Community', 'New']]
        image_root = Path(settings.BASE_DIR) / 'static' / 'images'
        source_images = sorted(list((image_root / 'posters').glob('*')) + list((image_root / 'hero_section').glob('*')))
        media_dir = Path(settings.MEDIA_ROOT) / 'seed-assets'
        media_dir.mkdir(parents=True, exist_ok=True)
        local_images = []
        for image in source_images:
            target = media_dir / image.name
            if not target.exists():
                shutil.copy2(image, target)
            local_images.append(target)
        image_names = [str(path.relative_to(settings.MEDIA_ROOT)).replace('\\', '/') for path in local_images]
        hero_images = [path for path in image_names if 'hero' in Path(path).name]
        if hero_images:
            for index, category in enumerate(categories.values()):
                category.cover_image = hero_images[index % len(hero_images)]
                category.save(update_fields=['cover_image'])
        content_items = []
        kinds = ['article', 'video', 'audio', 'image']
        for cat_name, category in categories.items():
            for index in range(5):
                title = f'{cat_name} Original Feature {index + 1}'
                slug = slugify(title)
                content, _ = Content.objects.get_or_create(slug=slug, defaults={
                    'title': title, 'category': category, 'content_type': kinds[index % 4],
                    'description': f'A fictional Fan Hub Plus feature for the {cat_name} community.',
                    'body': f'An original community story about {title}.',
                    'release_date': timezone.now() - timedelta(days=index * 9),
                    'popularity_score': 100 - index * 7, 'view_count': index * 3,
                    'source_type': 'embed' if kinds[index % 4] == 'video' else 'upload',
                    'video_url': 'https://www.youtube.com/embed/aqz-KE-bpKQ' if kinds[index % 4] == 'video' else '',
                    'is_published': True, 'created_by': users['admin'],
                    'thumbnail': image_names[(index + len(content_items)) % len(image_names)] if image_names else '',
                })
                content.genres.set(genres[:2])
                content.tags.set(tags)
                content_items.append(content)

        for cat_name, category in categories.items():
            for index in range(2):
                CharacterProfile.objects.get_or_create(name=f'{cat_name} Original Character {index + 1}', defaults={
                    'category': character_categories[cat_name], 'bio': 'An original fictional community character.',
                    'source_title': f'{cat_name} Stories', 'is_published': True,
                    'image': image_names[index % len(image_names)] if image_names else '',
                })

        merch_tags = [MerchTag.objects.get_or_create(slug=slugify(name), defaults={'name': name})[0] for name in ['Limited Edition', 'Pre-Order', 'Collectible']]
        for cat_name in self.categories:
            for index in range(2):
                item, _ = Merch.objects.get_or_create(name=f'{cat_name} Artisan Display {index + 1}', defaults={
                    'description': 'A fictional, display-only collectible concept.',
                    'franchise': f'{cat_name} Originals', 'sub_label': 'Studio edition',
                    'fandom': category,
                    'category': ['figures', 'apparel', 'props'][index % 3],
                    'price': '24.99', 'is_upcoming': index == 1, 'is_published': True,
                    'image': image_names[(index + 1) % len(image_names)] if image_names else '',
                })
                item.fandom = category
                item.save(update_fields=['fandom'])
                item.tags.set(merch_tags[:2])

        cities = ['Lagos', 'Nairobi', 'Accra']
        for index in range(9):
            title = f'Fan Hub Gathering {index + 1}'
            Event.objects.get_or_create(map_code=f'fan-gathering-{index + 1}', defaults={
                'title': title, 'description': 'A fictional community meetup.',
                'event_type': 'Community convention', 'category': categories[self.categories[index % 8]],
                'venue': f'Community Hall {index + 1}', 'city': cities[index % 3],
                'latitude': [6.5244, -1.2921, 5.6037][index % 3],
                'longitude': [3.3792, 36.8219, -0.1870][index % 3],
                'start_datetime': timezone.now() + timedelta(days=index + 1),
                'end_datetime': timezone.now() + timedelta(days=index + 2),
                'date_badge': f'DAY {index + 1}', 'price': '0.00',
                'status_line': 'Community registration open',
                'ticket_link': 'https://example.com/community-event',
                'highlights': 'Original creators\\nCommunity showcases',
                'is_published': True,
                'image': image_names[index % len(image_names)] if image_names else '',
            })
        for category in categories.values():
            EventHighlight.objects.get_or_create(title=f'{category.name} Story Spotlight', defaults={
                'category': category, 'body': 'A fictional community milestone.',
                'event_date': date.today(), 'display_order': 1,
                'image': image_names[0] if image_names else '',
            })

        faq, _ = ChatbotFAQ.objects.get_or_create(question='How do I save a story?', defaults={
            'keyword': 'bookmark, save, favorite', 'answer': 'Open a story while signed in and choose Save.',
            'category': categories['Anime'], 'is_active': True,
        })
        sample = content_items[0]
        Bookmark.objects.get_or_create(user=users['demo_user'], content_type=ContentType.objects.get_for_model(Content), object_id=sample.pk, defaults={'note': 'Read this later'})
        Rating.objects.get_or_create(user=users['demo_user'], media=sample, defaults={'rating': 5})
        Feedback.objects.get_or_create(user=users['demo_user'], subject='Demo feedback', defaults={'type': 'suggestion', 'severity': 'low', 'message': 'A seeded example for staff review.'})
        FanSubmission.objects.get_or_create(user=users['demo_user'], title='A community story idea', defaults={
            'category': categories['Comics'], 'body': 'A fictional pending submission for moderation.',
            'status': ApprovalStatus.PENDING, 'image': image_names[0] if image_names else '',
        })

        for name, user in users.items():
            self.stdout.write(f'{name}: {self.passwords[name]}')
        self.stdout.write('Counts: ' + ', '.join([
            f'categories={Category.objects.count()}',
            f'character_categories={CharacterCategory.objects.count()}',
            f'content={Content.objects.count()}',
            f'characters={CharacterProfile.objects.count()}',
            f'merch={Merch.objects.count()}',
            f'events={Event.objects.count()}',
            f'users={User.objects.count()}',
            f'profiles={Profile.objects.count()}',
            f'faq={ChatbotFAQ.objects.count()}',
            f'bookmarks={Bookmark.objects.count()}',
            f'ratings={Rating.objects.count()}',
            f'feedback={Feedback.objects.count()}',
            f'pending_submissions={FanSubmission.objects.filter(status=ApprovalStatus.PENDING).count()}',
        ]))
