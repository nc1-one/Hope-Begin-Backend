import re
from zoneinfo import ZoneInfo

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Count, F, Q, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models.functions import TruncDate

from apps.prayers.models import Prayer
from apps.hopecasts.models import Hopecast, HopecastPlayLog, HopecastCategory
from apps.daily_hope.models import HopeJourney, HopefulBeginningCompletion
from django.contrib.auth import get_user_model
from common.email_copy import LANGUAGES
from common.throttles import AnalyticsClickThrottle
from .models import DailyClick, ExternalClick

User = get_user_model()

MANILA = ZoneInfo('Asia/Manila')

# Prayer requests and Daily Hope sign-ups carry the language of the page
# they came from since the site started sending it, on 31 October 2026.
# Earlier ones were all saved as English, so they count under "before".
LANGUAGES_RECORDED_FROM = datetime(2026, 10, 31, 11, 30, tzinfo=MANILA)


def by_language(queryset):
    """How many rows in each language, plus "before" for rows from before
    languages were recorded."""
    counts = dict.fromkeys(LANGUAGES, 0)
    known = queryset.filter(created_at__gte=LANGUAGES_RECORDED_FROM)
    for row in known.values('lang').annotate(count=Count('id')):
        counts[row['lang']] = counts.get(row['lang'], 0) + row['count']
    counts['before'] = queryset.filter(created_at__lt=LANGUAGES_RECORDED_FROM).count()
    return counts


class AnalyticsView(APIView):
    """
    Prayer requests, HopeCast plays and Daily Hope for a date range, on
    Manila days like the visit counts. With ?lang=, prayer requests and
    Daily Hope are for that language only; HopeCast plays and the five
    steps have no language and always count every visitor.
    """

    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        with timezone.override(MANILA):
            return self.get_in_manila(request)

    def get_in_manila(self, request):
        start_date_str = request.query_params.get('start_date')
        end_date_str = request.query_params.get('end_date')
        lang = request.query_params.get('lang') or None
        today = timezone.localdate()

        try:
            if start_date_str:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            else:
                start_date = today - timedelta(days=30)

            if end_date_str:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            else:
                end_date = today
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)
        if lang is not None and lang not in LANGUAGES:
            return Response({"error": f"lang must be one of {', '.join(LANGUAGES)}."}, status=400)

        # Date range filtering
        all_prayers = Prayer.objects.filter(created_at__date__range=[start_date, end_date])
        play_log_qs = HopecastPlayLog.objects.filter(played_at__date__range=[start_date, end_date])
        all_journeys = HopeJourney.objects.filter(created_at__date__range=[start_date, end_date])
        all_finished = HopeJourney.objects.filter(finished_at__date__range=[start_date, end_date])
        completion_qs = HopefulBeginningCompletion.objects.filter(created_at__date__range=[start_date, end_date])

        def in_lang(queryset):
            if lang is None:
                return queryset
            return queryset.filter(lang=lang, created_at__gte=LANGUAGES_RECORDED_FROM)

        prayer_qs = in_lang(all_prayers)
        journey_qs = in_lang(all_journeys)
        finished_qs = in_lang(all_finished)

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
                # The two below, mixed: kept for the dashboard before 1
                # November 2026.
                "total_completions": total_completions + journey_completions,
                # Finished the five steps on /get-started.
                "hopeful_beginning_completions": total_completions,
                # Got every Daily Hope email.
                "daily_hope_finished": finished_qs.count(),
            },
            "prayers_by_category": list(prayers_by_category),
            "plays_by_category": list(plays_by_category),
            "subscribers_trend": subscribers_trend,
            # Every language side by side for these dates, whatever ?lang= is.
            "by_language": {
                "prayers": by_language(all_prayers),
                "daily_hope_signups": by_language(all_journeys),
                "daily_hope_finished": by_language(all_finished),
            },
            # Not tied to the dates: who gets Daily Hope today.
            "daily_hope_receiving": by_language(HopeJourney.objects.filter(is_active=True)),
            "languages_recorded_from": LANGUAGES_RECORDED_FROM.isoformat(),
            "lang": lang,
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
        
        # "war_room" before taps carried their page's language, then
        # "war_room__en", "war_room__ko" and so on.
        war_room_users = (
            ExternalClick.objects.filter(
                Q(link_name='war_room') | Q(link_name__startswith='war_room__')
            ).aggregate(total=Sum('clicks'))['total']
            or 0
        )

        return Response({
            "subscribers": subscribers,
            "listeners": listeners,
            "journeys": journeys,
            "carriers": carriers,
            "prayers": prayers,
            "lives_touched": lives_touched,
            "war_room_users": war_room_users
        })

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
