from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Sum, Count
from django.utils.crypto import get_random_string
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, permissions, viewsets, pagination, filters
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from django.utils import timezone
from datetime import timedelta
from django.db.models.functions import TruncDate

from apps.prayers.models import Prayer
from apps.hopecasts.models import Hopecast, HopecastPlayLog
from apps.daily_hope.models import HopefulBeginningCompletion
from apps.prayers.serializers import PrayerSerializer
from .serializers import (
    AdminRegistrationSerializer, 
    MyTokenObtainPairSerializer, 
    UserRegistrationSerializer,
    UserSerializer,
    AdminUserSerializer,
    StaffUserSerializer,
    AdminTeamSerializer,
    AddStaffAdminSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    CarrierApplicationSerializer
)
from .permissions import (
    ADMIN_ROLES,
    CanManageUser,
    IsOwnerOrAdmin,
    IsSuperAdmin,
    is_admin_team,
    is_superadmin,
)
from .tasks import send_admin_invite_email, send_approval_email, send_password_reset_email

User = get_user_model()

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            response = Response(None, status=status.HTTP_205_RESET_CONTENT)
            response.message = "Logged out successfully."
            return response
        except Exception:
            return Response(
                {"error": "Invalid token or token already blacklisted."},
                status=status.HTTP_400_BAD_REQUEST
            )

class RegistrationView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            response = Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
            response.message = "Registration successful. Pending admin approval."
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from common.throttles import StrictPublicFormThrottle

class CarrierApplicationView(APIView):
    permission_classes = (permissions.AllowAny,)
    throttle_classes = [StrictPublicFormThrottle]

    def post(self, request):
        serializer = CarrierApplicationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            response = Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
            response.message = "Your application is being reviewed. If approved, we will send a temporary password to your email."
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminRegistrationView(APIView):
    # Only a super admin can create another super admin.
    permission_classes = (IsSuperAdmin,)

    def post(self, request):
        serializer = AdminRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            response = Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
            response.message = "Admin registered successfully."
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().annotate(prayer_count=Count('assigned_prayers'))
    serializer_class = UserSerializer
    pagination_class = UserPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['first_name', 'last_name', 'email']
    filterset_fields = ['role', 'is_approved']
    ordering_fields = ['first_name', 'last_name', 'email', 'date_joined', 'prayer_count']
    ordering = ['-date_joined']
    
    def get_serializer_class(self):
        if is_superadmin(self.request.user):
            return AdminUserSerializer
        if is_admin_team(self.request.user):
            return StaffUserSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [permissions.IsAdminUser()]
        if self.action in ['retrieve', 'partial_update', 'update']:
            return [permissions.IsAuthenticated(), IsOwnerOrAdmin()]
        if self.action == 'destroy':
            return [permissions.IsAdminUser(), CanManageUser()]
        if self.action == 'create':
            return [IsSuperAdmin()]
        if self.action in ['me', 'my_profile', 'overview']:
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    def perform_destroy(self, instance):
        # A removed carrier's open requests go back to New, so the team can
        # give them to someone else.
        if instance.role == 'carrier':
            instance.assigned_prayers.filter(status__in=['ASSIGNED', 'ON_PROGRESS']).update(
                status='NEW', assigned_to=None
            )
        instance.delete()

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def overview(self, request):
        # 1. Total Prayers
        total_prayers = Prayer.objects.count()
        
        # 2. Pending (New) Prayers
        pending_prayers = Prayer.objects.filter(status='NEW').count()
        
        # 3. Approved Hope Carriers
        total_carriers = User.objects.filter(role='carrier', is_approved=True).count()
        
        # 4. Total HopeCast Plays
        total_hopecast_plays = Hopecast.objects.aggregate(total=Sum('play_count'))['total'] or 0
        
        # 5. Recent Prayer Requests (Top 5)
        recent_prayers = Prayer.objects.all().order_by('-created_at')[:5]
        recent_prayers_data = PrayerSerializer(recent_prayers, many=True).data

        # 6. Total Hope Carrier accounts, excluding admins and regular users
        total_users = User.objects.filter(role='carrier').count()

        # 7. Hopeful Beginning Completions
        journey_completions = HopefulBeginningCompletion.objects.count()

        # 8. Weekly Trends (Last 7 days)
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=6)

        # Prayer Trend
        prayers_by_date = Prayer.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        ).annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(count=Count('id')).order_by('date')
        
        prayer_trend = []
        for i in range(7):
            current_date = start_date + timedelta(days=i)
            day_name = current_date.strftime('%a')
            count = next((item['count'] for item in prayers_by_date if item['date'] == current_date), 0)
            prayer_trend.append({"day": day_name, "count": count})

        # Hopecast Play Trend
        plays_by_date = HopecastPlayLog.objects.filter(
            played_at__date__gte=start_date,
            played_at__date__lte=end_date
        ).annotate(
            date=TruncDate('played_at')
        ).values('date').annotate(count=Count('id')).order_by('date')
        
        hopecast_trend = []
        for i in range(7):
            current_date = start_date + timedelta(days=i)
            day_name = current_date.strftime('%a')
            count = next((item['count'] for item in plays_by_date if item['date'] == current_date), 0)
            hopecast_trend.append({"day": day_name, "count": count})

        data = {
            "total_prayers": total_prayers,
            "pending_prayers": pending_prayers,
            "total_carriers": total_carriers,
            "hopecast_plays": total_hopecast_plays,
            "total_users": total_users,
            "journey_completions": journey_completions,
            "recent_prayers": recent_prayers_data,
            "prayer_trend": prayer_trend,
            "hopecast_trend": hopecast_trend,
        }
        
        response = Response(data)
        response.message = "Dashboard overview data retrieved successfully."
        return response

    @action(detail=False, methods=['get', 'patch'], url_path='me')
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        elif request.method == 'PATCH':
            serializer = self.get_serializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser, CanManageUser])
    def approve(self, request, pk=None):
        user = self.get_object()
        user.is_approved = True
        
        # If it's a carrier, generate a temporary password and send email
        if user.role == 'carrier':
            temp_password = get_random_string(12)
            user.set_password(temp_password)
            user.save()
            
            # Send email asynchronously using Celery
            send_approval_email.delay(user.id, temp_password)
            message_response = "Carrier approved and credentials email will be sent shortly via background task."
        else:
            user.save()
            message_response = "User approved successfully."

        response = Response(UserSerializer(user).data)
        response.message = message_response
        return response

class AdminTeamView(APIView):
    """The super admin sees everyone on the admin team and adds staff admins."""
    permission_classes = (IsSuperAdmin,)

    def get(self, request):
        team = User.objects.filter(role__in=ADMIN_ROLES).order_by('-is_active', 'role', 'first_name', 'email')
        response = Response(AdminTeamSerializer(team, many=True).data)
        response.message = "Admin team retrieved successfully."
        return response

    def post(self, request):
        serializer = AddStaffAdminSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.save()
        send_admin_invite_email.delay(user.id, _inviter_name(request.user))
        response = Response(AdminTeamSerializer(user).data, status=status.HTTP_201_CREATED)
        response.message = f"Invite sent to {user.email}."
        return response


class AdminTeamMemberView(APIView):
    """Send a new invite link, or take away someone's admin access."""
    permission_classes = (IsSuperAdmin,)

    def post(self, request, pk, task):
        user = get_object_or_404(User, pk=pk, role__in=ADMIN_ROLES)

        if task == 'resend':
            if not user.is_active:
                return Response(
                    {"detail": "This person no longer has access. Add them again instead."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            send_admin_invite_email.delay(user.id, _inviter_name(request.user))
            response = Response(AdminTeamSerializer(user).data)
            response.message = f"A new link was sent to {user.email}."
            return response

        if user == request.user:
            return Response(
                {"detail": "You can't remove your own access."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if user.role == 'admin':
            # A super admin can't be added back from the admin team page.
            return Response(
                {"detail": "Super admins can't be removed here."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.is_active = False
        user.is_staff = False
        user.save(update_fields=['is_active', 'is_staff'])
        # Sign them out everywhere: no new access tokens from old refresh tokens.
        for token in OutstandingToken.objects.filter(user=user):
            BlacklistedToken.objects.get_or_create(token=token)
        response = Response(AdminTeamSerializer(user).data)
        response.message = f"{user.email} no longer has admin access."
        return response


def _inviter_name(user):
    return user.get_full_name() or user.email


class ForgotPasswordView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Reset URL (frontend URL)
            reset_url = f"{settings.FRONTEND_URL}/reset-password?uid={uidb64}&token={token}"
            
            # Send email asynchronously using Celery
            send_password_reset_email.delay(email, reset_url)
            response = Response(None)
            response.message = "Password reset link sent to email."
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response = Response(None)
            response.message = "Password has been reset successfully."
            return response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
