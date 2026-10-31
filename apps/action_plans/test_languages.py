import re
import time

from django.core import mail
from django.core.cache import cache
from django.test import SimpleTestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from common.email_copy import LANGUAGES, copy_for, site_path
from common.email_parts import crisis_text
from common.helplines import COUNTRY_HELP, LANGUAGE_COUNTRY

from .models import PlanCheckIn
from .tasks import manila_today, send_due_check_ins
from .tests import plan_payload

DASH = re.compile('[–—]')


class EmailCopyTests(SimpleTestCase):
    """Every language has every piece of every email, written to the copy rules."""

    def test_every_language_has_every_key(self):
        english = copy_for('en')
        for lang in LANGUAGES:
            module = copy_for(lang)
            self.assertEqual(module.__name__.rsplit('.', 1)[1], lang)
            for part in ('PLAN', 'DAILY', 'PRAYER'):
                with self.subTest(lang=lang, part=part):
                    words = getattr(module, part)
                    self.assertEqual(set(words), set(getattr(english, part)))
                    for key, text in words.items():
                        self.assertTrue(text.strip(), f'{lang} {part}.{key} is empty')
                        self.assertIsNone(DASH.search(text), f'{lang} {part}.{key} has a dash')
                        if lang in ('fr', 'de', 'es', 'ko'):
                            self.assertNotIn('!', text, f'{lang} {part}.{key}')

    def test_placeholders_match_english(self):
        english = copy_for('en')
        for lang in LANGUAGES:
            for part in ('PLAN', 'DAILY', 'PRAYER'):
                for key, text in getattr(english, part).items():
                    with self.subTest(lang=lang, key=key):
                        theirs = getattr(copy_for(lang), part)[key]
                        self.assertEqual(set(re.findall(r'\{\w+\}', theirs)), set(re.findall(r'\{\w+\}', text)))

    def test_crisis_line_follows_the_country_then_the_language(self):
        self.assertIn('3114', crisis_text('fr'))
        self.assertIn('109', crisis_text('ko'))
        # Korea's mental health crisis line comes after the suicide line.
        self.assertLess(crisis_text('ko').index('109'), crisis_text('ko').index('1577-0199'))
        self.assertIn('0800 111 0 111', crisis_text('de'))
        self.assertIn('800 911 2000', crisis_text('es'))
        self.assertIn('1553', crisis_text('en'))
        # A French reader in Belgium gets the Belgian line.
        self.assertIn('0800 32 123', crisis_text('fr', 'BE'))
        # Somewhere the site has no line: the directory and the emergency number.
        self.assertIn('findahelpline.com', crisis_text('de', 'ZZ'))
        for lang in LANGUAGES:
            line = COUNTRY_HELP[LANGUAGE_COUNTRY[lang]]
            self.assertIn(line.emergency, crisis_text(lang))

    def test_site_paths(self):
        self.assertEqual(site_path('en', '/action-plan'), '/action-plan')
        self.assertEqual(site_path('fr', '/action-plan'), '/fr/action-plan')
        self.assertEqual(site_path('ko', '/'), '/ko')
        self.assertEqual(site_path('tl', '/'), '/')


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class NewLanguageEmailTests(APITestCase):
    def setUp(self):
        cache.clear()

    def test_plan_email_in_every_language(self):
        for lang in LANGUAGES:
            mail.outbox.clear()
            cache.clear()
            c = copy_for(lang).PLAN
            payload = plan_payload(lang=lang, email=f'{lang}@example.com')
            payload['sections'].insert(0, {
                'heading': c['safety_heading'],
                'items': [{'title': '1.', 'detail': ''}],
            })
            response = self.client.post(reverse('action-plan-email'), payload, format='json')
            with self.subTest(lang=lang):
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                message = mail.outbox[0]
                html = message.alternatives[0][0]
                self.assertEqual(message.subject, c['plan_subject'])
                self.assertIn(f'https://hopebegins.today{site_path(lang, "/action-plan")}', message.body)
                if lang in ('en', 'tl'):
                    self.assertIn('m.me/', html)
                    self.assertLess(html.index('Ang safety plan mo' if lang == 'tl' else 'Your safety plan'), html.index('m.me/'))
                else:
                    # No e-coach: the help page in their language instead.
                    self.assertNotIn('m.me/', html)
                    self.assertNotIn('Messenger', message.body)
                    self.assertIn(f'https://hopebegins.today/{lang}/help', html)
                    self.assertLess(html.index(c['safety_heading']), html.index(f'/{lang}/help'))

    def test_plan_email_uses_the_phone_country(self):
        response = self.client.post(
            reverse('action-plan-email'), plan_payload(lang='fr', country='ch'), format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('143', mail.outbox[0].body)
        self.assertIn('tel:143', mail.outbox[0].alternatives[0][0])
        self.assertNotIn('3114', mail.outbox[0].body)

    def test_rejects_a_country_that_is_not_a_code(self):
        response = self.client.post(
            reverse('action-plan-email'), plan_payload(country='France'), format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_check_in_keeps_language_and_country(self):
        self.client.post(
            reverse('action-plan-check-in'),
            {'email': 'mi@example.com', 'lang': 'es', 'country': 'CO', 'website': '',
             'startTime': int((time.time() - 10) * 1000)},
            format='json',
        )
        check_in = PlanCheckIn.objects.get()
        self.assertEqual((check_in.lang, check_in.country), ('es', 'CO'))
        PlanCheckIn.objects.update(send_on=manila_today())
        send_due_check_ins()

        message = mail.outbox[0]
        self.assertEqual(message.subject, copy_for('es').PLAN['check_in_subject'])
        self.assertIn('106', message.body)
        self.assertIn('https://hopebegins.today/es/action-plan', message.body)
        self.assertIn('https://hopebegins.today/es/help', message.body)
        self.assertNotIn('m.me/', message.body)
