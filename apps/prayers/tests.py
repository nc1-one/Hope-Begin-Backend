from unittest import mock

from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APITestCase

from apps.users.tasks import send_assignment_notification_email, send_prayer_encouragement_email
from common.email_copy import copy_for

from .models import Prayer


class PrayedForYouEmailTests(TestCase):
    @mock.patch('apps.prayers.signals.send_prayer_encouragement_email')
    def test_completed_prayer_sends_a_plain_email(self, task):
        prayer = Prayer.objects.create(title='Ana', email='ana@example.com', content='Please pray for my mom.')
        task.delay.assert_not_called()

        prayer.status = 'COMPLETED'
        prayer.save()

        to_email, subject, message, lang = task.delay.call_args.args
        self.assertEqual(lang, 'en')
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


class PrayedForYouInEveryLanguageTests(TestCase):
    @mock.patch('apps.prayers.signals.send_prayer_encouragement_email')
    def test_email_follows_the_request_language_and_country(self, task):
        prayer = Prayer.objects.create(
            title='Mi-rae', email='m@example.com', content='Please pray for me.', lang='ko', country='KR'
        )
        prayer.status = 'COMPLETED'
        prayer.save()

        to_email, subject, message, lang = task.delay.call_args.args
        self.assertEqual(lang, 'ko')
        self.assertEqual(subject, copy_for('ko').PRAYER['subject'])
        self.assertIn('109', message)
        self.assertIn('https://hopebegins.today/ko/help', message)
        self.assertNotIn('m.me/', message)

    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_the_email_itself_has_no_english_footer(self):
        send_prayer_encouragement_email('m@example.com', 'Sujet', 'Bonjour Camille,', 'fr')
        message = mail.outbox[0]
        self.assertIn('https://hopebegins.today/fr', message.body)
        self.assertNotIn('Visit HopeBegins', message.body)
        self.assertIn('<html lang="fr">', message.alternatives[0][0])


class WhoSeesPrayerRequestsTests(APITestCase):
    """Requests hold names, emails and private worries: the admin team sees
    them all, a Hope Carrier only theirs, and no one else any."""

    def setUp(self):
        from django.contrib.auth import get_user_model
        from django.core.cache import cache

        cache.clear()
        User = get_user_model()

        def user(email, role, **extra):
            return User.objects.create_user(
                username=email, email=email, password='not-a-real-password-1', role=role,
                is_approved=True, is_staff=role in ('admin', 'staff'), **extra
            )

        self.staff = user('staff@example.com', 'staff')
        self.carrier = user('carrier@example.com', 'carrier')
        self.other_carrier = user('other@example.com', 'carrier')
        self.waiting_carrier = user('waiting@example.com', 'carrier', )
        self.waiting_carrier.is_approved = False
        self.waiting_carrier.save()
        self.mine = Prayer.objects.create(
            title='Ana', email='ana@example.com', content='Please pray for my mom.',
            status='ASSIGNED', assigned_to=self.carrier, lang='es', country='MX',
        )
        self.hidden_name = Prayer.objects.create(
            title='Ben', email='ben@example.com', content='Pray for me.', share_first_name=False,
            status='ASSIGNED', assigned_to=self.carrier,
        )
        self.theirs = Prayer.objects.create(
            title='Cy', email='cy@example.com', content='Pray for my job.',
            status='ASSIGNED', assigned_to=self.other_carrier,
        )
        self.new = Prayer.objects.create(title='Di', email='di@example.com', content='Pray for us.')

    def sign_in(self, user):
        from rest_framework_simplejwt.tokens import RefreshToken

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(user).access_token}')

    def results(self, response):
        data = response.data.get('data', response.data)
        return data.get('results', data) if isinstance(data, dict) else data

    def dashboard_url(self, user):
        return reverse('prayer-request-carrier-dashboard', kwargs={'user_id': str(user.pk)})

    def test_strangers_see_nothing(self):
        for url in [reverse('prayer-request-list'), self.dashboard_url(self.carrier),
                    reverse('prayer-request-detail', args=[self.mine.pk])]:
            self.assertIn(self.client.get(url).status_code, (401, 403), url)

    def test_a_carrier_sees_only_their_requests_without_emails(self):
        self.sign_in(self.carrier)
        rows = self.results(self.client.get(reverse('prayer-request-list')))
        self.assertEqual({row['id'] for row in rows}, {str(self.mine.pk), str(self.hidden_name.pk)})
        for row in rows:
            self.assertNotIn('email', row)
        names = {row['id']: row['title'] for row in rows}
        self.assertEqual(names[str(self.mine.pk)], 'Ana')
        self.assertEqual(names[str(self.hidden_name.pk)], '')

    def test_a_carrier_cannot_open_another_carriers_dashboard(self):
        self.sign_in(self.carrier)
        self.assertEqual(self.client.get(self.dashboard_url(self.other_carrier)).status_code, 403)
        mine = self.client.get(self.dashboard_url(self.carrier))
        self.assertEqual(mine.status_code, 200)
        data = mine.data.get('data', mine.data)
        self.assertEqual(len(data['available']), 2)

    def test_a_carrier_cannot_edit_delete_or_assign(self):
        self.sign_in(self.carrier)
        detail = reverse('prayer-request-detail', args=[self.mine.pk])
        self.assertEqual(self.client.patch(detail, {'status': 'NEW'}, format='json').status_code, 403)
        self.assertEqual(self.client.delete(detail).status_code, 403)
        assign = reverse('prayer-request-assign', args=[self.new.pk])
        self.assertEqual(self.client.post(assign, {'carrier_id': str(self.carrier.pk)}, format='json').status_code, 403)
        self.assertTrue(Prayer.objects.filter(pk=self.mine.pk, status='ASSIGNED').exists())

    def test_a_carrier_cannot_pray_for_someone_elses_request(self):
        self.sign_in(self.carrier)
        url = reverse('prayer-request-mark-prayed', args=[self.theirs.pk])
        self.assertEqual(self.client.post(url, {}, format='json').status_code, 404)

    def test_a_carrier_waiting_for_approval_sees_nothing(self):
        Prayer.objects.filter(pk=self.new.pk).update(assigned_to=self.waiting_carrier, status='ASSIGNED')
        self.sign_in(self.waiting_carrier)
        self.assertEqual(self.client.get(reverse('prayer-request-list')).status_code, 403)

    def test_the_team_sees_everything_with_language_and_country(self):
        self.sign_in(self.staff)
        rows = self.results(self.client.get(reverse('prayer-request-list'), {'lang': 'es'}))
        self.assertEqual([row['id'] for row in rows], [str(self.mine.pk)])
        self.assertEqual((rows[0]['lang'], rows[0]['country'], rows[0]['email']), ('es', 'MX', 'ana@example.com'))

    def test_the_end_date_includes_the_whole_day(self):
        self.sign_in(self.staff)
        today = self.new.created_at.date().isoformat()
        rows = self.results(self.client.get(
            reverse('prayer-request-list'), {'created_at__date__gte': today, 'created_at__date__lte': today}
        ))
        self.assertEqual(len(rows), 4)

    def test_only_approved_carriers_can_be_assigned(self):
        self.sign_in(self.staff)
        url = reverse('prayer-request-assign', args=[self.new.pk])
        waiting = self.client.post(url, {'carrier_id': str(self.waiting_carrier.pk)}, format='json')
        self.assertEqual(waiting.status_code, 404)
        approved = self.client.post(url, {'carrier_id': str(self.carrier.pk)}, format='json')
        self.assertEqual(approved.status_code, 200)

    def test_only_the_team_changes_organizations(self):
        from .models import Organization

        self.sign_in(self.carrier)
        url = reverse('organization-list')
        self.assertEqual(self.client.post(url, {'name': 'Church'}, format='json').status_code, 403)
        self.sign_in(self.staff)
        self.assertEqual(self.client.post(url, {'name': 'Church'}, format='json').status_code, 201)
        self.assertTrue(Organization.objects.filter(name='Church').exists())

    def test_removing_a_carrier_returns_their_open_requests(self):
        self.sign_in(self.staff)
        from .models import PrayerResponse

        PrayerResponse.objects.create(prayer=self.mine, user=self.carrier, content='Praying for you.')
        url = reverse('user-detail', args=[self.carrier.pk])
        self.assertEqual(self.client.delete(url).status_code, 204)
        self.mine.refresh_from_db()
        self.assertEqual((self.mine.status, self.mine.assigned_to), ('NEW', None))
        # The note they wrote stays with the request.
        self.assertTrue(PrayerResponse.objects.filter(prayer=self.mine).exists())
