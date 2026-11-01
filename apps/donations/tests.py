from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Donation

User = get_user_model()


class FinancialsTests(APITestCase):
    def setUp(self):
        cache.clear()
        owner = User.objects.create_user(
            username='owner@example.com', email='owner@example.com', password='not-a-real-password-1',
            role='admin', is_staff=True, is_approved=True,
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(owner).access_token}')

    def overview(self):
        response = self.client.get(reverse('donation-overview'))
        return response.data.get('data', response.data)

    def test_only_money_that_arrived_counts(self):
        Donation.objects.create(name='Ana', email='ana@example.com', amount=500, status='COMPLETED')
        Donation.objects.create(name='Ana', email='ANA@example.com', amount=300, status='COMPLETED')
        Donation.objects.create(name='Anonymous', amount=1000, status='MANUAL_BANK')
        Donation.objects.create(name='Anonymous', amount=200, status='MANUAL_BANK')
        Donation.objects.create(name='Ben', email='ben@example.com', amount=250, status='COMPLETED', donation_type='MONTHLY')
        # Opened checkouts that were never paid, or failed.
        Donation.objects.create(name='Cy', email='cy@example.com', amount=9000, status='PENDING')
        Donation.objects.create(name='Di', email='di@example.com', amount=700, status='FAILED')

        data = self.overview()
        self.assertEqual(data['totalRaised'], 2250)
        # Ana once by email, two gifts with no email, Ben.
        self.assertEqual(data['totalDonors'], 4)
        self.assertEqual((data['monthlyTotal'], data['monthlyDonors']), (250, 1))
        self.assertEqual(data['avgDonation'], 450)
        self.assertEqual((data['giftCount'], data['pendingCount']), (5, 1))

    def test_a_gift_added_by_hand_is_a_bank_transfer_on_its_day(self):
        response = self.client.post(reverse('donation-list'), {
            'name': 'Church group', 'amount': '1500.00', 'donation_type': 'ONE_TIME', 'date': '2026-10-20',
        }, format='json')
        self.assertEqual(response.status_code, 201)
        gift = Donation.objects.get(name='Church group')
        self.assertEqual((gift.status, gift.date.isoformat()), ('MANUAL_BANK', '2026-10-20'))

    def test_stripe_gifts_cannot_be_changed_by_hand(self):
        gift = Donation.objects.create(name='Ana', amount=500, status='COMPLETED', stripe_session_id='cs_test_1')
        url = reverse('donation-detail', args=[gift.pk])
        self.assertEqual(self.client.patch(url, {'amount': '5000.00'}, format='json').status_code, 400)
        self.assertEqual(self.client.patch(url, {'name': 'Ana R.'}, format='json').status_code, 200)
