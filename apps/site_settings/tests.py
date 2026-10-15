from importlib import import_module

from django.apps import apps as django_apps
from django.test import TestCase

from apps.site_settings.models import JourneyContent

migration = import_module('apps.site_settings.migrations.0004_plainer_journey_copy')


class PlainerJourneyCopyTests(TestCase):
    def setUp(self):
        # Start from the copy as it was before the change.
        old = dict((new, old) for old, new in migration.CHANGES)
        content = JourneyContent.objects.create()
        content.page_subtitle = old[content.page_subtitle]
        for field in migration.JSON_FIELDS:
            setattr(content, field, migration.swap(getattr(content, field), old))
        content.save()

    def test_old_copy_is_replaced(self):
        migration.forwards(django_apps, None)
        content = JourneyContent.objects.get()
        self.assertEqual(content.page_subtitle, 'Five short steps for when you feel hopeless.')
        self.assertEqual(
            content.prayer_section['steps'][4]['text'],
            'I rest in You, Lord. Things are not okay right now, but You are with me. Amen.',
        )
        self.assertEqual(content.welcome_section['expectations'][1], 'A guided prayer')

    def test_text_edited_in_admin_is_kept(self):
        content = JourneyContent.objects.get()
        content.welcome_section = {**content.welcome_section, 'body': 'Written by the team.'}
        content.save()
        migration.forwards(django_apps, None)
        content.refresh_from_db()
        self.assertEqual(content.welcome_section['body'], 'Written by the team.')
        self.assertEqual(content.devotional_section['subtitle'], 'A short reading on hope.')

    def test_backwards_restores_old_copy(self):
        migration.forwards(django_apps, None)
        migration.backwards(django_apps, None)
        content = JourneyContent.objects.get()
        self.assertEqual(content.page_subtitle, 'A journey toward hope, one step at a time.')
