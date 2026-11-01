from unittest import mock

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.prayers.models import Prayer

User = get_user_model()


def make_user(email, role, **extra):
    defaults = {
        'username': email,
        'email': email,
        'password': 'not-a-real-password-1',
        'role': role,
        'is_approved': True,
        'is_staff': role in ('admin', 'staff'),
    }
    defaults.update(extra)
    return User.objects.create_user(**defaults)


class AdminTeamTests(APITestCase):
    team_url = reverse('admin_team')

    def setUp(self):
        cache.clear()
        self.superadmin = make_user('owner@example.com', 'admin', first_name='Genesis')
        self.staff = make_user('staff@example.com', 'staff')
        self.carrier = make_user('carrier@example.com', 'carrier', is_staff=False)

    def sign_in(self, user):
        token = RefreshToken.for_user(user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    # ── Who can add admins ──

    def test_strangers_cannot_create_admins(self):
        response = self.client.post(reverse('admin_registration'), {
            'username': 'x', 'email': 'x@example.com', 'password': 'pass-12345',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(User.objects.filter(email='x@example.com').exists())

    def test_staff_cannot_create_super_admins_or_see_the_team(self):
        self.sign_in(self.staff)
        response = self.client.post(reverse('admin_registration'), {
            'username': 'x', 'email': 'x@example.com', 'password': 'pass-12345',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.get(self.team_url).status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            self.client.post(self.team_url, {'first_name': 'A', 'email': 'a@example.com'}).status_code,
            status.HTTP_403_FORBIDDEN,
        )

    @mock.patch('apps.users.views.send_admin_invite_email.delay')
    def test_super_admin_adds_a_staff_admin(self, invite):
        self.sign_in(self.superadmin)
        response = self.client.post(self.team_url, {
            'first_name': 'Ana', 'last_name': 'Cruz', 'email': 'Ana@Example.com',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        ana = User.objects.get(email='ana@example.com')
        self.assertEqual(ana.role, 'staff')
        self.assertTrue(ana.is_staff and ana.is_approved and ana.is_active)
        self.assertFalse(ana.is_superuser)
        self.assertFalse(ana.has_usable_password())
        invite.assert_called_once_with(ana.id, 'Genesis')
        self.assertFalse(response.data['has_password'])

        listed = self.client.get(self.team_url).data
        self.assertEqual(
            {person['email'] for person in listed},
            {'owner@example.com', 'staff@example.com', 'ana@example.com'},
        )

    @mock.patch('apps.users.views.send_admin_invite_email.delay')
    def test_cannot_add_an_email_that_already_has_an_account(self, invite):
        self.sign_in(self.superadmin)
        response = self.client.post(self.team_url, {
            'first_name': 'C', 'email': 'carrier@example.com',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.carrier.refresh_from_db()
        self.assertEqual(self.carrier.role, 'carrier')
        invite.assert_not_called()

    # ── What staff admins can see ──

    def test_staff_cannot_see_the_financials(self):
        self.sign_in(self.staff)
        self.assertEqual(
            self.client.get('/api/donations/').status_code, status.HTTP_403_FORBIDDEN
        )
        self.assertEqual(
            self.client.get('/api/donations/overview/').status_code, status.HTTP_403_FORBIDDEN
        )

        self.sign_in(self.superadmin)
        self.assertEqual(
            self.client.get('/api/donations/overview/').status_code, status.HTTP_200_OK
        )

    @mock.patch('apps.prayers.signals.send_prayer_encouragement_email.delay')
    def test_staff_see_the_dashboard_and_every_prayer(self, _email):
        Prayer.objects.create(title='A', email='a@example.com', content='x', status='COMPLETED')
        self.sign_in(self.staff)

        self.assertEqual(self.client.get('/api/users/overview/').status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.get('/api/analytics/clicks/').status_code, status.HTTP_200_OK)
        prayers = self.client.get('/api/prayers/requests/')
        self.assertEqual(prayers.status_code, status.HTTP_200_OK)
        self.assertEqual(prayers.data['count'], 1)

    def test_staff_cannot_raise_their_own_role(self):
        self.sign_in(self.staff)
        self.client.patch('/api/users/me/', {'role': 'admin'}, format='json')
        self.client.patch(f'/api/users/{self.staff.id}/', {'role': 'admin'}, format='json')
        self.staff.refresh_from_db()
        self.assertEqual(self.staff.role, 'staff')

    def test_staff_manage_carriers_but_not_admins(self):
        self.sign_in(self.staff)
        self.assertEqual(
            self.client.delete(f'/api/users/{self.superadmin.id}/').status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(
            self.client.delete(f'/api/users/{self.carrier.id}/').status_code,
            status.HTTP_204_NO_CONTENT,
        )
        self.assertTrue(User.objects.filter(id=self.superadmin.id).exists())

    def test_carriers_cannot_delete_users(self):
        self.sign_in(self.carrier)
        self.assertEqual(
            self.client.delete(f'/api/users/{self.superadmin.id}/').status_code,
            status.HTTP_403_FORBIDDEN,
        )

    # ── Taking access away ──

    def test_removing_an_admin_signs_them_out(self):
        refresh = RefreshToken.for_user(self.staff)
        self.sign_in(self.superadmin)
        response = self.client.post(reverse('admin_team_remove', args=[self.staff.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.staff.refresh_from_db()
        self.assertFalse(self.staff.is_active or self.staff.is_staff)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        self.assertEqual(
            self.client.get('/api/users/overview/').status_code, status.HTTP_401_UNAUTHORIZED
        )
        self.client.credentials()
        self.assertNotEqual(
            self.client.post('/api/users/token/refresh/', {'refresh': str(refresh)}).status_code,
            status.HTTP_200_OK,
        )

    def test_super_admin_cannot_remove_themselves(self):
        self.sign_in(self.superadmin)
        response = self.client.post(reverse('admin_team_remove', args=[self.superadmin.id]))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.superadmin.refresh_from_db()
        self.assertTrue(self.superadmin.is_active)

    def test_super_admins_cannot_be_removed(self):
        other_owner = make_user('owner2@example.com', 'admin')
        self.sign_in(self.superadmin)
        url = reverse('admin_team_remove', args=[other_owner.pk])
        self.assertEqual(self.client.post(url).status_code, status.HTTP_400_BAD_REQUEST)
        other_owner.refresh_from_db()
        self.assertTrue(other_owner.is_active and other_owner.is_staff)

    def test_remove_only_works_on_admins(self):
        self.sign_in(self.superadmin)
        response = self.client.post(reverse('admin_team_remove', args=[self.carrier.id]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @mock.patch('apps.users.views.send_admin_invite_email.delay')
    def test_a_removed_admin_can_be_added_back(self, invite):
        self.sign_in(self.superadmin)
        self.client.post(reverse('admin_team_remove', args=[self.staff.id]))
        response = self.client.post(self.team_url, {
            'first_name': 'Back', 'email': 'staff@example.com',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.staff.refresh_from_db()
        self.assertTrue(self.staff.is_active and self.staff.is_staff)
        self.assertFalse(self.staff.has_usable_password())
        invite.assert_called_once()

    @mock.patch('apps.users.views.send_admin_invite_email.delay')
    def test_resend_link(self, invite):
        self.sign_in(self.superadmin)
        response = self.client.post(reverse('admin_team_resend', args=[self.staff.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        invite.assert_called_once_with(self.staff.id, 'Genesis')

    # ── Signing in ──

    def test_staff_admin_can_sign_in(self):
        response = self.client.post('/api/users/login/', {
            'email': 'staff@example.com', 'password': 'not-a-real-password-1',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['role'], 'staff')
        self.staff.refresh_from_db()
        self.assertIsNotNone(self.staff.last_login)


class AdminInviteEmailTests(APITestCase):
    @mock.patch('apps.users.tasks.send_notification_email')
    def test_invite_links_to_setting_a_password(self, send):
        from .tasks import send_admin_invite_email

        user = make_user('ana@example.com', 'staff', first_name='Ana')
        send_admin_invite_email(user.id, 'Genesis')

        subject, message, recipients = send.call_args.args
        self.assertEqual(recipients, ['ana@example.com'])
        self.assertIn('Hi Ana', message)
        self.assertIn('Genesis added you', message)
        self.assertNotIn('—', message)
        path = send.call_args.kwargs['path']
        self.assertTrue(path.startswith('/reset-password?uid='))
        self.assertTrue(path.endswith('&for=admin'))
        self.assertEqual(send.call_args.kwargs['button_label'], 'Set your password')

    def test_other_emails_keep_the_usual_footer(self):
        from common.utils import append_visit_site_text, plain_text_to_html

        self.assertIn('Visit HopeBegins:', append_visit_site_text('Hello', '/'))
        self.assertIn('Visit HopeBegins', plain_text_to_html('Hello', '/'))
        self.assertIn('Set your password', plain_text_to_html('Hi', '/x', 'Set your password'))
