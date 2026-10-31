import re
import time
from unittest import mock

from django.core import mail
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from common.email_copy import LANGUAGES, copy_for

from .journey import FIELDS, LAST_DAY, day_in
from .models import EmailTemplate, HopeJourney
from .tasks import build_day_email, send_subscriber_email_logic

DASH = re.compile('[–—]')


class JourneyContentTests(SimpleTestCase):
    def test_every_language_has_every_day(self):
        for lang in LANGUAGES:
            for day in range(1, LAST_DAY + 1):
                with self.subTest(lang=lang, day=day):
                    content = day_in(lang, day)
                    for field in FIELDS:
                        self.assertTrue(content[field].strip(), f'{lang} day {day} has no {field}')
                        self.assertIsNone(DASH.search(content[field]), f'{lang} day {day} {field} has a dash')
                    self.assertNotIn('\n', content['opening'].replace('\n\n', ''))
                    if lang in ('fr', 'de', 'es', 'ko'):
                        for field in FIELDS:
                            if field != 'verse':
                                self.assertNotIn('!', content[field], f'{lang} day {day} {field}')
                    if lang == 'ko':
                        self.assertNotIn('하느님', ''.join(content.values()))

    def test_no_day_past_the_last(self):
        self.assertIsNone(day_in('fr', LAST_DAY + 1))


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class DailyHopeEmailTests(TestCase):
    def subscriber(self, **fields):
        return HopeJourney.objects.create(
            first_name='Mina', last_name='', email=f"{fields.get('lang', 'en')}@example.com", **fields
        )

    def test_each_language_gets_its_own_day(self):
        for lang in LANGUAGES:
            mail.outbox.clear()
            subscriber = self.subscriber(lang=lang)
            self.assertTrue(send_subscriber_email_logic(subscriber))
            message = mail.outbox[0]
            day = day_in(lang, 1)
            with self.subTest(lang=lang):
                self.assertIn(day['title'], message.subject)
                self.assertIn(day['verse_ref'], message.body)
                self.assertIn(day['verse'], message.body)
                self.assertIn(f'/api/daily-hope/stop/{subscriber.id}/', message.extra_headers['List-Unsubscribe'])
                self.assertIn('<html lang=', message.alternatives[0][0])
            subscriber.refresh_from_db()
            self.assertEqual(subscriber.current_day, 2)

    def test_crisis_line_follows_the_country(self):
        subscriber = self.subscriber(lang='de', country='AT')
        _, text, _ = build_day_email(subscriber, 3)
        self.assertIn('142', text)

    def test_last_day_finishes(self):
        subscriber = self.subscriber(lang='ko', current_day=LAST_DAY)
        self.assertTrue(send_subscriber_email_logic(subscriber))
        subscriber.refresh_from_db()
        self.assertFalse(subscriber.is_active)
        self.assertIsNotNone(subscriber.finished_at)

    def test_dashboard_template_is_for_english_only(self):
        EmailTemplate.objects.create(day_number=1, subject='From the dashboard', html_content='<html><body>Hi</body></html>')
        english = self.subscriber(lang='en')
        send_subscriber_email_logic(english)
        self.assertEqual(mail.outbox[-1].subject, 'From the dashboard')
        self.assertIn('/api/daily-hope/stop/', mail.outbox[-1].alternatives[0][0])

        french = self.subscriber(lang='fr')
        send_subscriber_email_logic(french)
        self.assertIn(day_in('fr', 1)['title'], mail.outbox[-1].subject)


class StopDailyHopeTests(TestCase):
    def setUp(self):
        self.subscriber = HopeJourney.objects.create(
            first_name='Ana', last_name='', email='ana@example.com', lang='es'
        )
        self.url = reverse('daily-hope-stop', args=[self.subscriber.id])

    def test_opening_the_link_only_asks(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, copy_for('es').DAILY['stop_confirm'])
        self.assertContains(response, '<form method="post"')
        self.subscriber.refresh_from_db()
        self.assertTrue(self.subscriber.is_active)

    def test_the_button_or_one_tap_unsubscribe_stops(self):
        response = self.client.post(self.url, {'List-Unsubscribe': 'One-Click'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, copy_for('es').DAILY['stopped_title'])
        self.subscriber.refresh_from_db()
        self.assertFalse(self.subscriber.is_active)

    def test_unknown_link(self):
        response = self.client.get(reverse('daily-hope-stop', args=['00000000-0000-0000-0000-000000000000']))
        self.assertEqual(response.status_code, 404)


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class SignUpTests(APITestCase):
    @mock.patch('apps.daily_hope.tasks.send_welcome_and_day_one.delay')
    def test_sign_up_keeps_language_and_country(self, delay):
        response = self.client.post(
            reverse('hope-journey-list'),
            {'first_name': 'Jun', 'last_name': '', 'email': 'jun@example.com', 'lang': 'ko', 'country': 'kr',
             'start_time': int((time.time() - 10) * 1000)},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(response.data['message'], copy_for('ko').DAILY['welcome'])
        subscriber = HopeJourney.objects.get()
        self.assertEqual((subscriber.lang, subscriber.country), ('ko', 'KR'))
        delay.assert_called_once()


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class SignUpAgainTests(APITestCase):
    def payload(self, **fields):
        return {'first_name': 'Ana', 'email': 'Ana@Example.com', 'lang': 'fr',
                'start_time': int((time.time() - 10) * 1000), **fields}

    @mock.patch('apps.daily_hope.tasks.send_welcome_and_day_one.delay')
    def test_someone_who_stopped_starts_again_at_day_one(self, delay):
        HopeJourney.objects.create(first_name='Ana', email='ana@example.com', current_day=9, is_active=False)
        response = self.client.post(reverse('hope-journey-list'), self.payload(), format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        subscriber = HopeJourney.objects.get()
        self.assertEqual((subscriber.current_day, subscriber.is_active, subscriber.lang), (1, True, 'fr'))
        delay.assert_called_once_with(subscriber.id)

    @mock.patch('apps.daily_hope.tasks.send_welcome_and_day_one.delay')
    def test_signing_up_twice_keeps_the_day(self, delay):
        HopeJourney.objects.create(first_name='Ana', email='ana@example.com', current_day=5)
        response = self.client.post(reverse('hope-journey-list'), self.payload(lang='de'), format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        subscriber = HopeJourney.objects.get()
        self.assertEqual((subscriber.current_day, subscriber.lang), (5, 'de'))
        delay.assert_not_called()


class DashboardTemplateTests(APITestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model

        admin = get_user_model().objects.create_superuser(username='admin', email='admin@example.com', password='test-only-pass')
        self.client.force_authenticate(admin)
        self.template = EmailTemplate.objects.create(
            day_number=3, subject='Old day 3', html_content='<p>old</p>', is_active=False
        )
        self.url = reverse('email-template-detail', args=[self.template.id])

    def test_each_day_shows_the_built_in_email(self):
        data = self.client.get(reverse('email-template-list')).data[0]
        self.assertIn(day_in('en', 3)['title'], data['builtin_subject'])
        self.assertIn(day_in('en', 3)['verse'], data['builtin_html'])

    def test_saving_words_makes_them_the_day_email(self):
        self.client.patch(self.url, {'subject': 'Mine', 'html_content': '<p>mine</p>'}, format='json')
        self.template.refresh_from_db()
        self.assertTrue(self.template.is_active)

    def test_switching_back_to_the_built_in_day(self):
        self.template.is_active = True
        self.template.save()
        self.client.patch(self.url, {'is_active': False}, format='json')
        self.template.refresh_from_db()
        self.assertFalse(self.template.is_active)
