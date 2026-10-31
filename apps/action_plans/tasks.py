import logging
from datetime import timedelta
from zoneinfo import ZoneInfo

from celery import shared_task
from django.utils import timezone

from .emails import send_check_in_email
from .models import PlanCheckIn

logger = logging.getLogger(__name__)

MANILA = ZoneInfo('Asia/Manila')
# A check-in that still fails this long after its date is dropped.
GIVE_UP_AFTER_DAYS = 7


def manila_today():
    return timezone.localdate(timezone=MANILA)


@shared_task
def send_due_check_ins():
    today = manila_today()
    due = PlanCheckIn.objects.filter(
        sent_at__isnull=True, send_on__lte=today
    ).exclude(email='')
    for check_in in due:
        try:
            send_check_in_email(
                check_in.email, check_in.first_name, check_in.lang, check_in.country
            )
        except Exception:
            logger.exception('Failed to send plan check-in %s', check_in.pk)
            if check_in.send_on < today - timedelta(days=GIVE_UP_AFTER_DAYS):
                check_in.email = ''
                check_in.first_name = ''
                check_in.save(update_fields=['email', 'first_name'])
            continue
        check_in.email = ''
        check_in.first_name = ''
        check_in.sent_at = timezone.now()
        check_in.save(update_fields=['email', 'first_name', 'sent_at'])
