from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Prayer, PrayerResponse
from apps.users.tasks import send_prayer_encouragement_email
from apps.action_plans.emails import ECOACH_APP_URL, ECOACH_WEB_URL
from common.email_copy import ECOACH_LANGUAGES, copy_for, site_path
from common.email_parts import crisis_text
from common.utils import get_site_url
import logging

logger = logging.getLogger(__name__)

@receiver(pre_save, sender=Prayer)
def capture_old_status(sender, instance, **kwargs):
    try:
        old_instance = Prayer.objects.get(pk=instance.pk)
        instance._old_status = old_instance.status
    except Prayer.DoesNotExist:
        instance._old_status = None

@receiver(post_save, sender=Prayer)
def send_prayer_notification(sender, instance, created, **kwargs):
    # Check if status changed to COMPLETED
    old_status = getattr(instance, '_old_status', None)
    
    if instance.status == 'COMPLETED' and old_status != 'COMPLETED':
        logger.info(f"Prayer {instance.id} marked as COMPLETED. Sending notification email.")
        
        # 1. Prepare the email in the language of the page they asked from.
        # The title field holds the requester's name.
        lang = instance.lang
        c = copy_for(lang).PRAYER
        name = (instance.title or '').strip()
        greeting = c['greeting'].format(name=name) if name else c['greeting_no_name']
        subject = c['subject']
        # The request itself is not quoted: email previews can be seen by
        # others, and the person already knows what they asked.
        message = f"{greeting}\n\n{c['prayed']}\n\n"

        # 2. Look for the latest encouragement note (PrayerResponse)
        latest_response = PrayerResponse.objects.filter(prayer=instance).order_by('-created_at').first()
        if latest_response:
            message += (
                f"{c['note']}\n"
                f"--------------------------------------------------\n"
                f"\"{latest_response.content}\"\n"
                f"--------------------------------------------------\n\n"
            )

        # Someone to talk to: the e-coach speaks English and Filipino; other
        # languages get their country's free lines.
        if lang in ECOACH_LANGUAGES:
            someone = f"{c['ecoach']} {ECOACH_APP_URL}\n{c['ecoach_computer']} {ECOACH_WEB_URL}"
        else:
            someone = f"{c['help']} {get_site_url(site_path(lang, '/help'))}"
        message += (
            f"{c['praying_with_you']} {someone}\n\n"
            f"{crisis_text(lang, instance.country)}\n\n"
            f"{c['sign_off']}"
        )

        # 3. Send email asynchronously using Celery
        send_prayer_encouragement_email.delay(instance.email, subject, message)
