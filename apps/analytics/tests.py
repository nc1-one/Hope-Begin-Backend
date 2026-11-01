from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import DailyClick, ExternalClick
from .views import LANGUAGES_RECORDED_FROM, MANILA
from django.utils import timezone


class RecordClickTests(APITestCase):
    url = reverse('record-click')

    def setUp(self):
        cache.clear()

    def test_counts_all_time_and_today(self):
        self.client.post(self.url, {'link_name': 'visit_home'}, format='json')
        response = self.client.post(self.url, {'link_name': 'visit_home'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ExternalClick.objects.get(link_name='visit_home').clicks, 2)
        daily = DailyClick.objects.get(link_name='visit_home')
        self.assertEqual(daily.count, 2)
        self.assertEqual(daily.date, timezone.localdate(timezone=MANILA))

    def test_accepts_the_names_the_site_uses(self):
        for name in ['ecoach_feeling_pagod-na-ako_top', 'menu_feeling_anxious', 'visit_feeling_how-to-calm-anxiety']:
            response = self.client.post(self.url, {'link_name': name}, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK, name)

    def test_rejects_junk_names(self):
        for name in ['', 'Visit Home', '<script>', 'x' * 81, None]:
            response = self.client.post(self.url, {'link_name': name}, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, name)
        self.assertFalse(ExternalClick.objects.exists())


class ClickAnalyticsTests(APITestCase):
    url = reverse('click-analytics')

    def setUp(self):
        cache.clear()
        self.admin = get_user_model().objects.create_user(
            username='admin', email='admin@example.com', password='x', is_staff=True
        )
        today = timezone.localdate(timezone=MANILA)
        DailyClick.objects.create(link_name='visit_home', date=today, count=5)
        DailyClick.objects.create(link_name='visit_home', date=today - timedelta(days=1), count=3)
        DailyClick.objects.create(link_name='visit_home', date=today - timedelta(days=60), count=40)
        DailyClick.objects.create(link_name='tool_breathe_start', date=today, count=2)
        ExternalClick.objects.create(link_name='visit_home', clicks=48)

    def test_needs_an_admin(self):
        self.assertIn(
            self.client.get(self.url).status_code,
            (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN),
        )

    def test_totals_and_daily_for_the_range(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data.get('data', response.data)
        self.assertEqual(data['totals'], {'visit_home': 8, 'tool_breathe_start': 2})
        self.assertEqual(len([d for d in data['daily'] if d['link_name'] == 'visit_home']), 2)
        self.assertEqual(data['all_time']['visit_home'], 48)
        self.assertIsNotNone(data['tracked_since'])

    def test_custom_range_and_bad_dates(self):
        self.client.force_authenticate(self.admin)
        today = timezone.localdate(timezone=MANILA)
        start = (today - timedelta(days=90)).isoformat()
        response = self.client.get(self.url, {'start_date': start, 'end_date': today.isoformat()})
        data = response.data.get('data', response.data)
        self.assertEqual(data['totals']['visit_home'], 48)

        bad = self.client.get(self.url, {'start_date': 'yesterday'})
        self.assertEqual(bad.status_code, status.HTTP_400_BAD_REQUEST)


class WarRoomCountTests(APITestCase):
    def test_counts_taps_in_every_language(self):
        ExternalClick.objects.create(link_name='war_room', clicks=4)
        ExternalClick.objects.create(link_name='war_room__en', clicks=2)
        ExternalClick.objects.create(link_name='war_room__ko', clicks=1)
        ExternalClick.objects.create(link_name='war_roomy', clicks=9)
        admin = get_user_model().objects.create_superuser(username='a', email='a@example.com', password='test-only-pass')
        self.client.force_authenticate(admin)
        response = self.client.get(reverse('impact-analytics'))
        self.assertEqual(response.data['war_room_users'], 7)


class AnalyticsByLanguageTests(APITestCase):
    url = reverse('analytics-overview')

    def setUp(self):
        from apps.daily_hope.models import HopeJourney, HopefulBeginningCompletion
        from apps.prayers.models import Prayer

        self.admin = get_user_model().objects.create_user(
            username='admin', email='admin@example.com', password='x', is_staff=True
        )
        now = timezone.now()
        for lang in ['en', 'ko', 'ko', 'fr']:
            Prayer.objects.create(title='t', email='p@example.com', content='c', lang=lang)
        # Saved before languages were recorded: counts as before, not English.
        old = Prayer.objects.create(title='t', email='p@example.com', content='c')
        Prayer.objects.filter(pk=old.pk).update(created_at=LANGUAGES_RECORDED_FROM - timedelta(hours=1))
        HopeJourney.objects.create(first_name='a', email='a@example.com', lang='es')
        HopeJourney.objects.create(
            first_name='b', email='b@example.com', lang='ko', is_active=False, finished_at=now
        )
        HopefulBeginningCompletion.objects.create()
        self.client.force_authenticate(self.admin)

    def get(self, **params):
        start = (LANGUAGES_RECORDED_FROM - timedelta(days=2)).date().isoformat()
        response = self.client.get(self.url, {'start_date': start, **params})
        return response, response.data.get('data', response.data)

    def test_every_language_side_by_side(self):
        response, data = self.get()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        prayers = data['by_language']['prayers']
        self.assertEqual(prayers, {'en': 1, 'tl': 0, 'fr': 1, 'de': 0, 'es': 0, 'ko': 2, 'before': 1})
        self.assertEqual(data['by_language']['daily_hope_signups']['es'], 1)
        self.assertEqual(data['by_language']['daily_hope_finished']['ko'], 1)
        self.assertEqual(data['daily_hope_receiving']['es'], 1)
        self.assertEqual(data['daily_hope_receiving']['ko'], 0)
        self.assertEqual(data['summary']['total_prayers'], 5)
        self.assertEqual(data['summary']['hopeful_beginning_completions'], 1)
        self.assertEqual(data['summary']['daily_hope_finished'], 1)

    def test_one_language(self):
        _, data = self.get(lang='ko')
        self.assertEqual(data['summary']['total_prayers'], 2)
        self.assertEqual(data['summary']['total_new_subscribers'], 1)
        self.assertEqual(data['summary']['daily_hope_finished'], 1)
        # No language on these: every visitor.
        self.assertEqual(data['summary']['hopeful_beginning_completions'], 1)
        # The side-by-side counts stay the same.
        self.assertEqual(data['by_language']['prayers']['fr'], 1)

    def test_rejects_an_unknown_language(self):
        response, _ = self.get(lang='xx')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
