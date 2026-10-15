import time
from datetime import timedelta

from django.core import mail
from django.core.cache import cache
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import PlanCheckIn
from .tasks import manila_today, send_due_check_ins


def plan_payload(**overrides):
    payload = {
        'email': 'ana@example.com',
        'first_name': 'Ana',
        'summary': ['Some days of low mood.', 'Sleep that is off.'],
        'sections': [
            {
                'heading': 'Your daily tools',
                'intro': 'Start with one or two.',
                'items': [
                    {
                        'title': 'Slow your breathing',
                        'detail': 'Breathe in for 4, out for 6.',
                        'steps': ['Use it when you feel tense.'],
                    },
                    {
                        'title': 'Talk it through with Hope AI',
                        'detail': 'An AI assistant you can chat with at any hour.',
                        'link': '/hope-ai',
                        'link_label': 'Chat with Hope',
                    },
                ],
            },
        ],
        'website': '',
        'startTime': int((time.time() - 10) * 1000),
    }
    payload.update(overrides)
    return payload


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class EmailActionPlanTests(APITestCase):
    url = reverse('action-plan-email')

    def setUp(self):
        cache.clear()

    def test_sends_plan_email(self):
        response = self.client.post(self.url, plan_payload(), format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.to, ['ana@example.com'])
        self.assertEqual(message.subject, 'Your Hopeful Beginning Plan')
        html = message.alternatives[0][0]
        self.assertIn('Hi Ana,', html)
        self.assertIn('Slow your breathing', html)
        self.assertIn('https://m.me/352008124672499', html)
        self.assertIn('https://www.facebook.com/messages/t/352008124672499', html)
        self.assertIn('https://m.me/352008124672499', message.body)
        self.assertIn('1553', html)
        self.assertIn('https://hopebegins.today/hope-ai', html)
        self.assertIn('Chat with Hope', html)
        self.assertIn('Slow your breathing', message.body)

    def test_safety_plan_comes_first_then_ecoach(self):
        safety = {
            'heading': 'Your safety plan',
            'items': [{'title': '5. Crisis lines, open 24/7', 'detail': 'Call 1553.', 'link': 'tel:1553'}],
        }
        payload = plan_payload()
        payload['sections'] = payload['sections'] + [safety]

        self.client.post(self.url, payload, format='json')

        html = mail.outbox[0].alternatives[0][0]
        safety_at = html.index('Your safety plan')
        self.assertLess(safety_at, html.index('Your daily tools'))
        self.assertLess(safety_at, html.index('Want someone to journey with you?'))

    def test_escapes_html(self):
        payload = plan_payload(first_name='<b>Ana</b>')
        payload['sections'][0]['items'][0]['title'] = '<script>alert(1)</script>'

        self.client.post(self.url, payload, format='json')

        html = mail.outbox[0].alternatives[0][0]
        self.assertNotIn('<script>', html)
        self.assertIn('&lt;script&gt;', html)
        self.assertNotIn('<b>Ana</b>', html)

    def test_rejects_honeypot(self):
        response = self.client.post(self.url, plan_payload(website='spam'), format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(mail.outbox), 0)

    def test_rejects_form_sent_too_fast(self):
        payload = plan_payload(startTime=int(time.time() * 1000))
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(mail.outbox), 0)

    def test_rejects_protocol_relative_links(self):
        payload = plan_payload()
        payload['sections'][0]['items'][1]['link'] = '//evil.example.com'
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rejects_outside_links(self):
        payload = plan_payload()
        payload['sections'][0]['items'][1]['link'] = 'https://evil.example.com/login'
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(mail.outbox), 0)

    def test_rejects_spam_keywords(self):
        payload = plan_payload(summary=['Buy now and get crypto'])
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_limits_emails_per_address(self):
        for _ in range(3):
            response = self.client.post(self.url, plan_payload(), format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(self.url, plan_payload(), format='json')

        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertEqual(len(mail.outbox), 3)

    def test_name_is_not_spam_checked(self):
        response = self.client.post(self.url, plan_payload(first_name='Seo-yeon'), format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class PlanCheckInTests(APITestCase):
    url = reverse('action-plan-check-in')

    def setUp(self):
        cache.clear()

    def payload(self, **overrides):
        data = {
            'email': 'ana@example.com',
            'first_name': 'Ana',
            'website': '',
            'startTime': int((time.time() - 10) * 1000),
        }
        data.update(overrides)
        return data

    def test_schedules_one_check_in_a_week_out(self):
        response = self.client.post(self.url, self.payload(), format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        check_in = PlanCheckIn.objects.get()
        self.assertEqual(check_in.send_on, manila_today() + timedelta(days=7))
        self.assertEqual(check_in.first_name, 'Ana')
        self.assertEqual(len(mail.outbox), 0)

    def test_signing_up_again_does_not_add_a_second_email(self):
        self.client.post(self.url, self.payload(), format='json')
        self.client.post(self.url, self.payload(email='ANA@example.com', first_name='Ann'), format='json')

        self.assertEqual(PlanCheckIn.objects.count(), 1)
        self.assertEqual(PlanCheckIn.objects.get().first_name, 'Ann')

    def test_rejects_honeypot(self):
        response = self.client.post(self.url, self.payload(website='spam'), format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(PlanCheckIn.objects.exists())

    def test_task_sends_due_check_ins_and_deletes_the_address(self):
        today = manila_today()
        due = PlanCheckIn.objects.create(email='ana@example.com', first_name='Ana', send_on=today)
        later = PlanCheckIn.objects.create(email='ben@example.com', send_on=today + timedelta(days=3))

        send_due_check_ins()

        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.to, ['ana@example.com'])
        self.assertEqual(message.subject, 'How are you doing this week?')
        html = message.alternatives[0][0]
        self.assertIn('Hi Ana,', html)
        self.assertIn('/action-plan', html)
        self.assertIn('tel:1553', html)
        self.assertIn('deleted your email address', html)

        due.refresh_from_db()
        self.assertIsNotNone(due.sent_at)
        self.assertEqual(due.email, '')
        self.assertEqual(due.first_name, '')
        later.refresh_from_db()
        self.assertIsNone(later.sent_at)
        self.assertEqual(later.email, 'ben@example.com')

        send_due_check_ins()
        self.assertEqual(len(mail.outbox), 1)


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class TaglishEmailTests(APITestCase):
    def setUp(self):
        cache.clear()

    def test_plan_email_wrapper_follows_the_plan_language(self):
        payload = plan_payload(lang='tl')
        payload['sections'].insert(0, {
            'heading': 'Ang safety plan mo',
            'items': [{'title': '1. Kilalanin ang warning signs mo', 'detail': 'Isulat ang mga ito.'}],
        })
        response = self.client.post(reverse('action-plan-email'), payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        message = mail.outbox[0]
        self.assertEqual(message.subject, 'Ang Hopeful Beginning Plan mo')
        html = message.alternatives[0][0]
        self.assertIn('Ang ipinakita ng mga sagot mo', html)
        self.assertIn('Tumawag sa NCMH Crisis Hotline', html)
        # The safety plan still comes before the e-coach box.
        self.assertLess(html.index('Ang safety plan mo'), html.index('Kausapin ang e-coach'))

    def test_check_in_email_uses_the_language_chosen_at_sign_up(self):
        self.client.post(
            reverse('action-plan-check-in'),
            {'email': 'ana@example.com', 'lang': 'tl', 'website': '', 'startTime': int((time.time() - 10) * 1000)},
            format='json',
        )
        PlanCheckIn.objects.update(send_on=manila_today())
        send_due_check_ins()

        self.assertEqual(mail.outbox[0].subject, 'Kumusta ka ngayong linggo?')
        self.assertIn('Binura na namin ang email address mo', mail.outbox[0].body)

    def test_rejects_unknown_language(self):
        response = self.client.post(reverse('action-plan-email'), plan_payload(lang='fr'), format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
