from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.core.mail import send_mail
from django.conf import settings
from .models import Prayer, PrayerResponse, Organization
from .serializers import PrayerSerializer, AdminPrayerSerializer, PrayerResponseSerializer, OrganizationSerializer
from apps.users.permissions import ADMIN_ROLES, IsApproved
from apps.users.tasks import send_prayer_encouragement_email, send_assignment_notification_email

from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

from common.throttles import StrictPublicFormThrottle

class PrayerViewSet(viewsets.ModelViewSet):
    pagination_class = StandardResultsSetPagination
    throttle_classes = [StrictPublicFormThrottle]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'status': ['exact'],
        'category': ['exact'],
        'created_at': ['gte', 'lte'],
    }
    search_fields = ['title', 'content', 'email']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if user.role in ADMIN_ROLES:
                return Prayer.objects.all()
            if user.role == 'carrier':
                # Carriers see NEW prayers + prayers assigned to them
                from django.db.models import Q
                return Prayer.objects.filter(
                    Q(status='NEW') | Q(assigned_to=user)
                )
        # Public gets nothing for list (they use create)
        return Prayer.objects.filter(status='NEW')

    def get_serializer_class(self):
        # Admin gets full control serializer
        if self.request.user.is_authenticated and self.request.user.role in ADMIN_ROLES:
            return AdminPrayerSerializer
        # Public only gets the submission serializer
        return PrayerSerializer

    def get_permissions(self):
        # Allow anyone to submit a prayer
        if self.action == 'create':
            return [permissions.AllowAny()]
        # List and other management requires approval
        if self.action in ['list', 'retrieve', 'partial_update', 'update', 'destroy', 'assign', 'mark_prayed', 'claim']:
            return [permissions.IsAuthenticated(), IsApproved()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        # If user is authenticated, link the prayer to them
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save()

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def assign(self, request, pk=None):
        prayer = self.get_object()
        carrier_id = request.data.get('carrier_id')
        if carrier_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                carrier = User.objects.get(id=carrier_id, role='carrier')
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

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsApproved])
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

    @action(detail=False, methods=['get'], url_path='carrier-dashboard/(?P<user_id>[^/.]+)', permission_classes=[permissions.IsAuthenticated, IsApproved])
    def carrier_dashboard(self, request, user_id=None):
        # Get prayers specifically assigned to this user_id
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

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsApproved])
    def start_praying(self, request, pk=None):
        prayer = self.get_object()
        if prayer.assigned_to != request.user:
            return Response({"error": "You are not assigned to this prayer."}, status=status.HTTP_403_FORBIDDEN)
        prayer.status = 'ON_PROGRESS'
        prayer.save()
        response = Response(self.get_serializer(prayer).data)
        response.message = "Started praying."
        return response

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsApproved])
    def claim(self, request, pk=None):
        prayer = self.get_object()
        if prayer.status != 'NEW':
            return Response({"error": "This prayer is already assigned or completed."}, status=status.HTTP_400_BAD_REQUEST)
        
        prayer.assigned_to = request.user
        prayer.status = 'ASSIGNED'
        prayer.save()
        
        response = Response(self.get_serializer(prayer).data)
        response.message = "Prayer claimed successfully."
        return response

class PrayerResponseViewSet(viewsets.ModelViewSet):
    queryset = PrayerResponse.objects.all()
    serializer_class = PrayerResponseSerializer
    permission_classes = [permissions.IsAuthenticated, IsApproved]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    
    def get_permissions(self):
        if self.action == 'list':
            # Allow public to list active organizations for the dropdown
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsApproved()]

    def get_queryset(self):
        queryset = Organization.objects.all()
        # If not admin, only show active organizations
        if not (self.request.user.is_authenticated and self.request.user.role in ADMIN_ROLES):
            queryset = queryset.filter(is_active=True)
        return queryset
