from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Sum, Avg, Count
from django_filters.rest_framework import DjangoFilterBackend
from .models import Donation
from .serializers import DonationSerializer
from apps.users.permissions import IsSuperAdmin

class DonationPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class DonationViewSet(viewsets.ModelViewSet):
    queryset = Donation.objects.all()
    serializer_class = DonationSerializer
    pagination_class = DonationPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ('donation_type',)
    search_fields = ('name',)
    ordering_fields = ('date', 'amount', 'name')
    ordering = ('-date',)

    def get_permissions(self):
        # The financials are for super admins only.
        return [IsSuperAdmin()]

    @action(detail=False, methods=['get'])
    def overview(self, request):
        total_raised = Donation.objects.aggregate(Sum('amount'))['amount__sum'] or 0
        total_donors = Donation.objects.values('name').distinct().count()
        monthly_total = Donation.objects.filter(donation_type='MONTHLY').aggregate(Sum('amount'))['amount__sum'] or 0
        avg_donation = Donation.objects.aggregate(Avg('amount'))['amount__avg'] or 0
        
        return Response({
            'totalRaised': float(total_raised),
            'totalDonors': total_donors,
            'monthlyTotal': float(monthly_total),
            'avgDonation': round(float(avg_donation), 2)
        })
