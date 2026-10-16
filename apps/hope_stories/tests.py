from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .models import HopeStory

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


class HopeStoryPermissionTests(APITestCase):
    list_url = reverse('hope-story-list')
    approved_url = reverse('hope-story-approved')

    def setUp(self):
        cache.clear()
        self.superadmin = make_user('owner@example.com', 'admin')
        self.staff = make_user('staff@example.com', 'staff')
        self.carrier = make_user('carrier@example.com', 'carrier')

        self.pending = HopeStory.objects.create(full_name='Pending Story', testimonial='Waiting for review.')
        self.approved = HopeStory.objects.create(
            full_name='Approved Story', testimonial='Shared publicly.', status='APPROVED',
        )
        self.rejected = HopeStory.objects.create(
            full_name='Rejected Story', testimonial='Not shared.', status='REJECTED',
        )
        self.pending_url = reverse('hope-story-detail', args=[self.pending.id])

    def sign_in(self, user):
        token = RefreshToken.for_user(user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    def assert_locked_out(self, expected_status):
        self.assertEqual(self.client.get(self.list_url).status_code, expected_status)
        self.assertEqual(self.client.get(self.pending_url).status_code, expected_status)
        response = self.client.patch(self.pending_url, {'status': 'APPROVED'}, format='json')
        self.assertEqual(response.status_code, expected_status)
        self.assertEqual(self.client.delete(self.pending_url).status_code, expected_status)

        self.pending.refresh_from_db()
        self.assertEqual(self.pending.status, 'PENDING')

    # ── Who cannot manage stories ──

    def test_strangers_cannot_manage_stories(self):
        self.assert_locked_out(status.HTTP_401_UNAUTHORIZED)

    def test_carriers_cannot_manage_stories(self):
        self.sign_in(self.carrier)
        self.assert_locked_out(status.HTTP_403_FORBIDDEN)

    # ── The admin team manages stories ──

    def test_staff_admin_lists_and_approves_stories(self):
        self.sign_in(self.staff)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {story['id'] for story in response.data},
            {str(self.pending.id), str(self.approved.id), str(self.rejected.id)},
        )

        response = self.client.patch(self.pending_url, {'status': 'APPROVED'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.pending.refresh_from_db()
        self.assertEqual(self.pending.status, 'APPROVED')

    def test_super_admin_lists_rejects_and_deletes_stories(self):
        self.sign_in(self.superadmin)
        response = self.client.get(self.list_url, {'status': 'PENDING'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([story['id'] for story in response.data], [str(self.pending.id)])

        response = self.client.patch(self.pending_url, {'status': 'REJECTED'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.pending.refresh_from_db()
        self.assertEqual(self.pending.status, 'REJECTED')

        response = self.client.delete(self.pending_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(HopeStory.objects.filter(id=self.pending.id).exists())

    # ── What stays public ──

    def test_approved_stories_are_public_and_only_approved(self):
        response = self.client.get(self.approved_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([story['id'] for story in response.data], [str(self.approved.id)])
        self.assertNotIn('status', response.data[0])

    def test_anyone_can_submit_a_story_for_review(self):
        response = self.client.post(self.list_url, {
            'full_name': 'New Voice', 'testimonial': 'Hope found me.',
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        story = HopeStory.objects.get(full_name='New Voice')
        self.assertEqual(story.status, 'PENDING')
