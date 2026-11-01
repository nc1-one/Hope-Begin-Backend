from django.db.models import Count
from rest_framework import viewsets, permissions, status, filters
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.core.mail import send_mail
from django.conf import settings
from .models import Prayer, PrayerResponse, Organization
from .serializers import (
    AdminOrganizationSerializer,
    AdminPrayerSerializer,
    CarrierPrayerSerializer,
    OrganizationSerializer,
    PrayerResponseSerializer,
    PrayerSerializer,
)
from apps.users.permissions import (
    IsAdminTeam,
    IsAdminTeamOrCarrier,
    is_admin_team,
    is_approved_carrier,
)
from apps.users.tasks import send_prayer_encouragement_email, send_assignment_notification_email

from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

from common.throttles import StrictPublicFormThrottle

class PrayerViewSet(viewsets.ModelViewSet):
    """
    Anyone can send a prayer request. The admin team sees and manages every
    request; an approved Hope Carrier sees only the requests assigned to
    them, without the requester's email (CarrierPrayerSerializer).
    """

    pagination_class = StandardResultsSetPagination
    throttle_classes = [StrictPublicFormThrottle]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'status': ['exact'],
        'category': ['exact'],
        'lang': ['exact'],
        'country': ['exact'],
        'organization': ['exact'],
        'assigned_to': ['exact'],
        # date__ lookups include the whole end day; plain lte stops at its
        # first second.
        'created_at': ['gte', 'lte', 'date__gte', 'date__lte'],
    }
    search_fields = ['title', 'content', 'email']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    # What a Hope Carrier may do: see their requests and pray for them.
    CARRIER_ACTIONS = {'list', 'retrieve', 'mark_prayed', 'start_praying', 'carrier_dashboard'}

    def get_queryset(self):
        user = self.request.user
        if is_admin_team(user):
            return Prayer.objects.all()
        if is_approved_carrier(user):
            return Prayer.objects.filter(assigned_to=user)
        return Prayer.objects.none()

    def get_serializer_class(self):
        if self.action == 'create':
            return PrayerSerializer
        if is_admin_team(self.request.user):
            return AdminPrayerSerializer
        return CarrierPrayerSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        if self.action in self.CARRIER_ACTIONS:
            return [IsAdminTeamOrCarrier()]
        # Editing, deleting and assigning: the admin team only.
        return [IsAdminTeam()]

    def perform_create(self, serializer):
        # If user is authenticated, link the prayer to them
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save()

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        prayer = self.get_object()
        carrier_id = request.data.get('carrier_id')
        if carrier_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                # Only carriers the team has approved can be given a request.
                carrier = User.objects.get(
                    id=carrier_id, role='carrier', is_approved=True, is_active=True
                )
                prayer.assigned_to = carrier
                prayer.status = 'ASSIGNED'
                prayer.save()
                
                # Send email notification to carrier
                send_assignment_notification_email.delay(carrier.email)
                
                response = Response(AdminPrayerSerializer(prayer).data)
                response.message = f"Prayer assigned to {carrier.email} successfully."
                return response
            except User.DoesNotExist:
                return Response({"error": "Carrier not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"error": "carrier_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def mark_prayed(self, request, pk=None):
        prayer = self.get_object()
        note = request.data.get('note')
        
        # 1. If note is present, save it to the database
        if note:
            # Save the response in the database
            PrayerResponse.objects.create(
                prayer=prayer,
                user=request.user,
                content=note
            )
            
        # 2. Mark as completed
        prayer.status = 'COMPLETED'
        prayer.save()
        
        response = Response(self.get_serializer(prayer).data)
        response.message = "Prayer marked as completed. The requester has been notified."
        return response

    @action(detail=False, methods=['get'], url_path='carrier-dashboard/(?P<user_id>[^/.]+)')
    def carrier_dashboard(self, request, user_id=None):
        # A carrier sees only their own requests; the admin team may look at
        # any carrier's.
        if not is_admin_team(request.user) and user_id != str(request.user.pk):
            return Response(
                {"error": "You can only see the prayers assigned to you."},
                status=status.HTTP_403_FORBIDDEN,
            )
        prayers = Prayer.objects.filter(assigned_to_id=user_id)
        
        serializer = self.get_serializer(prayers, many=True)
        data = serializer.data
        
        # available - ASSIGNED status
        # my_prayers - ON_PROGRESS status
        # completed - COMPLETED status
        available = [p for p in data if p['status'] == 'ASSIGNED']
        my_prayers = [p for p in data if p['status'] == 'ON_PROGRESS']
        completed = [p for p in data if p['status'] == 'COMPLETED']
        
        return Response({
            "available": available,
            "my_prayers": my_prayers,
            "completed": completed,
            "stats": {
                "available": len(available),
                "my_prayers": len(my_prayers),
                "completed": len(completed)
            }
        })

    @action(detail=True, methods=['post'])
    def start_praying(self, request, pk=None):
        prayer = self.get_object()
        if prayer.assigned_to != request.user:
            return Response({"error": "You are not assigned to this prayer."}, status=status.HTTP_403_FORBIDDEN)
        prayer.status = 'ON_PROGRESS'
        prayer.save()
        response = Response(self.get_serializer(prayer).data)
        response.message = "Started praying."
        return response

class PrayerResponseViewSet(viewsets.ModelViewSet):
    """Notes carriers write for the requester: the team sees every note, a
    carrier only their own, on requests assigned to them."""

    serializer_class = PrayerResponseSerializer
    permission_classes = [IsAdminTeamOrCarrier]

    def get_queryset(self):
        if is_admin_team(self.request.user):
            return PrayerResponse.objects.all()
        return PrayerResponse.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        prayer = serializer.validated_data['prayer']
        if not is_admin_team(self.request.user) and prayer.assigned_to_id != self.request.user.pk:
            raise PermissionDenied("You can only write notes on prayers assigned to you.")
        serializer.save(user=self.request.user)

class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    
    def get_serializer_class(self):
        if is_admin_team(self.request.user):
            return AdminOrganizationSerializer
        return OrganizationSerializer

    def get_permissions(self):
        if self.action == 'list':
            # The prayer form looks up the organization in /prayers?org=<id>.
            return [permissions.AllowAny()]
        return [IsAdminTeam()]

    def get_queryset(self):
        queryset = Organization.objects.annotate(prayer_count=Count('prayers'))
        # Everyone but the admin team sees only active organizations.
        if not is_admin_team(self.request.user):
            queryset = queryset.filter(is_active=True)
        return queryset
