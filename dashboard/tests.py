from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from article.models import ApprovalStatus, FanSubmission
from catalog.models import Category, Content
from chatbot.models import ChatbotFAQ
from events.models import Event
from django.contrib.contenttypes.models import ContentType
from engagements.models import Bookmark


class StaffWorkflowsTests(TestCase):
    def setUp(self):
        self.client = Client(SERVER_NAME='127.0.0.1')
        self.staff = User.objects.create_user(username='staff', email='staff@example.test', password='safe-test-password', is_staff=True)
        self.category = Category.objects.create(name='Anime', slug='anime')
        self.assertTrue(self.client.login(username='staff', password='safe-test-password'))

    def test_admin_content_form_creates_real_content(self):
        response = self.client.post(reverse('admin_content_form'), {
            'title': 'Staff article', 'category': self.category.pk, 'content_type': 'article',
            'description': 'Staff-created content', 'body': 'Body text', 'genres': [], 'tags': [],
            'is_published': 'on',
        })
        self.assertRedirects(response, reverse('admin_content_form'))
        content = Content.objects.get(title='Staff article')
        self.assertTrue(content.is_published)
        self.assertEqual(content.created_by, self.staff)

    def test_faq_create_and_edit(self):
        data = {'question': 'How do I save?', 'keyword': 'save, bookmark', 'answer': 'Use the bookmark button.', 'category': self.category.pk, 'is_active': 'on'}
        self.assertRedirects(self.client.post(reverse('admin_chatbot_faq'), data), reverse('admin_chatbot_faq'))
        faq = ChatbotFAQ.objects.get(question='How do I save?')
        data.update({'faq_id': faq.pk, 'question': 'How do I bookmark?'})
        self.assertRedirects(self.client.post(reverse('admin_chatbot_faq'), data), reverse('admin_chatbot_faq'))
        self.assertTrue(ChatbotFAQ.objects.filter(pk=faq.pk, question='How do I bookmark?').exists())

    def test_submission_decision_records_reviewer_and_date(self):
        submitter = User.objects.create_user(username='fan', email='fan@example.test', password='safe-test-password')
        submission = FanSubmission.objects.create(user=submitter, category=self.category, title='Fan post', body='Fan work')
        response = self.client.post(reverse('admin_submissions'), {'submission_id': submission.pk, 'action': 'approve', 'review_note': 'Looks good'})
        self.assertRedirects(response, reverse('admin_submissions'))
        submission.refresh_from_db()
        self.assertEqual(submission.status, ApprovalStatus.APPROVED)
        self.assertEqual(submission.reviewed_by, self.staff)
        self.assertIsNotNone(submission.reviewed_at)

    def test_event_bookmark_is_listed_with_a_real_destination(self):
        event = Event.objects.create(title='Test convention', venue='Hall', city='Lagos')
        response = self.client.post(reverse('bookmark-toggle'), {
            'content_type_id': ContentType.objects.get_for_model(Event).pk,
            'object_id': event.pk,
            'note': 'Visit this one',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['bookmarked'])
        listing = self.client.get(reverse('bookmark-list'))
        self.assertContains(listing, event.title)
        self.assertContains(listing, f'/events/{event.pk}/')
