from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Sum, Avg, Count, Q
from django.db.models.functions import Lower
from django_filters.rest_framework import DjangoFilterBackend
from .models import Donation
from .serializers import DonationSerializer
from apps.users.permissions import IsSuperAdmin

class DonationPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

# Gifts that were paid, as opposed to checkouts that were only opened.
RECEIVED = ('COMPLETED', 'MANUAL_BANK')


class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer
    pagination_class = DonationPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ('donation_type', 'status')
    search_fields = ('name',)
    ordering_fields = ('date', 'amount', 'name')
    ordering = ('-date',)

    def get_permissions(self):
        # The financials are for super admins only.
        return [IsSuperAdmin()]

    def perform_create(self, serializer):
        # Gifts the team adds by hand are bank transfers that already arrived.
        serializer.save(status=serializer.validated_data.get('status') or 'MANUAL_BANK')

    @action(detail=False, methods=['get'])
    def overview(self, request):
        # Only money that arrived: paid through Stripe, or a bank transfer the
        # team recorded. A pending row is a checkout that was opened and may
        # never have been paid.
        received = Donation.objects.filter(status__in=RECEIVED)
        total_raised = received.aggregate(Sum('amount'))['amount__sum'] or 0
        # One donor per email address; a gift with no email is one donor.
        no_email = Q(email__isnull=True) | Q(email='')
        total_donors = (
            received.exclude(no_email).values(address=Lower('email')).distinct().count()
            + received.filter(no_email).count()
        )
        # Monthly gifts as set up. Stripe's later monthly payments and
        # cancellations aren't recorded yet, so this is what was promised.
        monthly = received.filter(donation_type='MONTHLY')
        monthly_total = monthly.aggregate(Sum('amount'))['amount__sum'] or 0
        avg_donation = received.aggregate(Avg('amount'))['amount__avg'] or 0

        return Response({
            'totalRaised': float(total_raised),
            'totalDonors': total_donors,
            'monthlyTotal': float(monthly_total),
            'monthlyDonors': monthly.count(),
            'avgDonation': round(float(avg_donation), 2),
            'giftCount': received.count(),
            'pendingCount': Donation.objects.filter(status='PENDING').count(),
        })
