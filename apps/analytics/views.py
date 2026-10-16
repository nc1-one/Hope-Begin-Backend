import re
from zoneinfo import ZoneInfo

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Count, F, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models.functions import TruncDate

from apps.prayers.models import Prayer
from apps.hopecasts.models import Hopecast, HopecastPlayLog, HopecastCategory
from apps.daily_hope.models import HopeJourney, HopefulBeginningCompletion
from django.contrib.auth import get_user_model
from common.throttles import AnalyticsClickThrottle
from .models import DailyClick, ExternalClick

User = get_user_model()

class AnalyticsView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')

        try:
            if start_date_str:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            else:
                start_date = (timezone.now() - timedelta(days=30)).date()

            if end_date_str:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            else:
                end_date = timezone.now().date()
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

        # Date range filtering
        prayer_qs = Prayer.objects.filter(created_at__date__range=[start_date, end_date])
        play_log_qs = HopecastPlayLog.objects.filter(played_at__date__range=[start_date, end_date])
        journey_qs = HopeJourney.objects.filter(created_at__date__range=[start_date, end_date])
        completion_qs = HopefulBeginningCompletion.objects.filter(created_at__date__range=[start_date, end_date])

        # 1. Prayers by Category
        prayers_by_category = prayer_qs.values('category').annotate(count=Count('id')).order_by('-count')
        # Map category keys to labels if needed, but the frontend can handle it too.

        # 2. Hopecast Plays by Category
        plays_by_category = HopecastCategory.objects.filter(
            hopecasts__play_logs__played_at__date__range=[start_date, end_date]
        ).annotate(
            count=Count('hopecasts__play_logs')
        ).values('name', 'count').order_by('-count')

        # 3. Daily Hope Subscribers (Trend)
        subscribers_trend_raw = journey_qs.annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(count=Count('id')).order_by('date')
        
        # Fill in gaps for trend
        subscribers_trend = []
        days_diff = (end_date - start_date).days + 1
        for i in range(days_diff):
            curr_date = start_date + timedelta(days=i)
            count = next((item['count'] for item in subscribers_trend_raw if item['date'] == curr_date), 0)
            subscribers_trend.append({
                "date": curr_date.strftime('%Y-%m-%d'),
                "count": count
            })

        # 4. Campaign Completions
        total_completions = completion_qs.count()
        # Also users who reached day 21 in this period
        journey_completions = HopeJourney.objects.filter(
            current_day__gte=21,
            updated_at__date__range=[start_date, end_date]
        ).count()

        # 5. Summary Stats
        data = {
            "summary": {
                "total_prayers": prayer_qs.count(),
                "total_plays": play_log_qs.count(),
                "total_new_subscribers": journey_qs.count(),
                "total_completions": total_completions + journey_completions,
            },
            "prayers_by_category": list(prayers_by_category),
            "plays_by_category": list(plays_by_category),
            "subscribers_trend": subscribers_trend,
            "date_range": {
                "start_date": start_date.strftime('%Y-%m-%d'),
                "end_date": end_date.strftime('%Y-%m-%d')
            }
        }

        return Response(data)


class ImpactAnalyticsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        # Following the plan in task-9-dynamic-impact-plan.md
        subscribers = HopeJourney.objects.filter(is_active=True).count()
        listeners = HopecastPlayLog.objects.count()
        # Total journeys initiated (all HopeJourney records)
        journeys = HopeJourney.objects.count()
        # Active carriers
        carriers = User.objects.filter(role='carrier', is_active=True).count()
        
        # Additional metrics for completeness
        prayers = Prayer.objects.count()
        
        lives_touched = subscribers + listeners + journeys + carriers
        
        try:
            war_room_click = ExternalClick.objects.get(link_name="war_room")
            war_room_users = war_room_click.clicks
        except ExternalClick.DoesNotExist:
            war_room_users = 0
            
        return Response({
            "subscribers": subscribers,
            "listeners": listeners,
            "journeys": journeys,
            "carriers": carriers,
            "prayers": prayers,
            "lives_touched": lives_touched,
            "war_room_users": war_room_users
        })

MANILA = ZoneInfo('Asia/Manila')
# Event names the site sends, like "visit_home" or "menu_feeling_anxious".
LINK_NAME = re.compile(r'^[a-z0-9][a-z0-9_\-]{0,79}$')


class RecordClickView(APIView):
    """Counts one anonymous event: no cookies, IPs or visitor details are kept."""

    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    throttle_classes = [AnalyticsClickThrottle]

    def post(self, request):
        link_name = request.data.get("link_name")
        if not isinstance(link_name, str) or not LINK_NAME.match(link_name):
            return Response(
                {"error": "link_name must be lowercase letters, numbers, - or _ (up to 80)."},
                status=400,
            )

        click, _ = ExternalClick.objects.get_or_create(link_name=link_name)
        ExternalClick.objects.filter(pk=click.pk).update(clicks=F('clicks') + 1)
        daily, _ = DailyClick.objects.get_or_create(
            link_name=link_name, date=timezone.localdate(timezone=MANILA)
        )
        DailyClick.objects.filter(pk=daily.pk).update(count=F('count') + 1)
        click.refresh_from_db(fields=['clicks'])

        return Response({"success": True, "clicks": click.clicks})


class ClickAnalyticsView(APIView):
    """
    Visits and tool use for the admin dashboard: totals and daily counts for
    a date range (Manila dates), plus all-time totals.
    """

    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        today = timezone.localdate(timezone=MANILA)
        try:
            start_date = datetime.strptime(
                request.query_params.get('start_date', ''), '%Y-%m-%d'
            ).date() if request.query_params.get('start_date') else today - timedelta(days=30)
            end_date = datetime.strptime(
                request.query_params.get('end_date', ''), '%Y-%m-%d'
            ).date() if request.query_params.get('end_date') else today
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

        rows = DailyClick.objects.filter(date__range=[start_date, end_date])
        totals = {
            row['link_name']: row['total']
            for row in rows.values('link_name').annotate(total=Sum('count'))
        }
        daily = [
            {"date": row['date'].isoformat(), "link_name": row['link_name'], "count": row['count']}
            for row in rows.order_by('date', 'link_name').values('date', 'link_name', 'count')
        ]
        first = DailyClick.objects.order_by('date').values_list('date', flat=True).first()

        return Response({
            "date_range": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
            "tracked_since": first.isoformat() if first else None,
            "totals": totals,
            "daily": daily,
            "all_time": {
                row['link_name']: row['clicks']
                for row in ExternalClick.objects.values('link_name', 'clicks')
            },
        })
