from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Prayer, PrayerResponse
from apps.users.tasks import send_prayer_encouragement_email
from apps.action_plans.emails import ECOACH_APP_URL, ECOACH_WEB_URL, crisis_text
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
        logger.info(f"Prayer {instance.id} marked as COMPLETED. Sending notification email to {instance.email}.")
        
        # 1. Prepare email content. The title field holds the requester's name.
        name = (instance.title or '').strip()
        greeting = f"Hi {name}," if name else "Hi,"
        subject = "A Hope Carrier prayed for you today"
        message = (
            f"{greeting}\n\n"
            f"A Hope Carrier prayed for your request today.\n\n"
            f"Your prayer request:\n"
            f"--------------------------------------------------\n"
            f"\"{instance.content}\"\n"
            f"--------------------------------------------------\n\n"
        )

        # 2. Look for the latest encouragement note (PrayerResponse)
        latest_response = PrayerResponse.objects.filter(prayer=instance).order_by('-created_at').first()
        if latest_response:
            message += (
                f"They wrote a note for you:\n"
                f"--------------------------------------------------\n"
                f"\"{latest_response.content}\"\n"
                f"--------------------------------------------------\n\n"
            )

        message += (
            "We're praying with you. If you'd like to talk to someone, "
            f"an e-coach is on Messenger: {ECOACH_APP_URL}\n"
            f"On a computer: {ECOACH_WEB_URL}\n\n"
            f"{crisis_text()}\n\n"
            "HopeBegins"
        )

        # 3. Send email asynchronously using Celery
        send_prayer_encouragement_email.delay(instance.email, subject, message)
