from unittest import mock

from django.test import TestCase

from apps.users.tasks import send_assignment_notification_email

from .models import Prayer


class PrayedForYouEmailTests(TestCase):
    @mock.patch('apps.prayers.signals.send_prayer_encouragement_email')
    def test_completed_prayer_sends_a_plain_email(self, task):
        prayer = Prayer.objects.create(title='Ana', email='ana@example.com', content='Please pray for my mom.')
        task.delay.assert_not_called()

        prayer.status = 'COMPLETED'
        prayer.save()

        to_email, subject, message = task.delay.call_args.args
        self.assertEqual(to_email, 'ana@example.com')
        self.assertEqual(subject, 'A Hope Carrier prayed for you today')
        self.assertIn('Hi Ana,', message)
        self.assertIn('A Hope Carrier prayed for your request today.', message)
        self.assertNotIn('Please pray for my mom.', message)
        self.assertIn('https://m.me/352008124672499', message)
        self.assertIn('1553', message)
        self.assertTrue(message.endswith('HopeBegins'))
        self.assertNotIn('!', message)
        self.assertNotIn('—', message)


class AssignmentEmailTests(TestCase):
    @mock.patch('apps.users.tasks.send_notification_email')
    def test_carrier_email_never_names_the_requester(self, send):
        send_assignment_notification_email('carrier@example.com', 'Ana')

        subject, message, recipients = send.call_args.args[:3]
        self.assertEqual(subject, 'A new prayer request for you')
        self.assertEqual(recipients, ['carrier@example.com'])
        self.assertNotIn('Ana', message)
        self.assertIn('/login/carrier', message)
