from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from .models import HopeJourney, EmailTemplate
from .content import GET_HOPE_DROPS_CONTENT
from common.utils import append_visit_site_html, append_visit_site_text, visit_site_html
import logging

logger = logging.getLogger(__name__)

def send_subscriber_email_logic(subscriber):
    """
    Internal logic to send a specific day's email to a subscriber
    and increment their progress.
    """
    day = subscriber.current_day
    logger.info(f"Processing Daily Hope email for {subscriber.email} (Day {day})")
    
    # Try to get from database first
    template = EmailTemplate.objects.filter(day_number=day, is_active=True).first()
    
    if template:
        subject = template.subject
        html_content = append_visit_site_html(template.html_content)
        # We need a plain text version. Since we don't store it, we'll use a generic one or strip HTML.
        # For now, let's just use a simple message as plain text fallback.
        text_content = append_visit_site_text(
            f"Day {day} of your Hope Journey is here. To read all of it, open this email in an app that shows formatting."
        )
    else:
        # Fallback to hardcoded content if no template found
        content = GET_HOPE_DROPS_CONTENT.get(day)
        
        if not content:
            # If no content for this day, we might have finished the 21nd day
            if day > 21:
                subscriber.is_active = False
                subscriber.finished_at = timezone.now()
                subscriber.save()
            return False
            
        subject = f"Day {day} of your Hope Journey: {content['title']}"
        
        # Plain text version
        text_content = append_visit_site_text(
            f"Day {day}: {content['title']}\n\n{content['description']}\n\n{content['verse']}\n\n{content.get('outro', '')}\n\nReflect:\n{content.get('reflection', '')}\n\nPrayer:\n{content.get('prayer', '')}\n\n{content.get('sign_off', 'Hope begins here,')}\nHopeBegins Team\n\nSupport: hopebegins.today/give-hope\nPrayers: hopebegins.today/prayers"
        )

        # HTML content with premium styling
        html_content = f"""
        <html>
            <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.8; color: #2d3748; background-color: #f7fafc; padding: 20px;">
                <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);">
                    <!-- Header Image -->
                    <div style="width: 100%; height: 200px; overflow: hidden;">
                        <img src="{content['image_url']}" alt="Daily Hope Day {day}" style="width: 100%; height: 100%; object-fit: cover;">
                    </div>

                    <div style="padding: 40px;">
                        <div style="text-transform: uppercase; letter-spacing: 0.1em; color: #a0aec0; font-weight: 700; font-size: 12px; margin-bottom: 8px;">Day {day}</div>
                        <h2 style="color: #2d3748; margin-top: 0; font-size: 28px; line-height: 1.2;">{content['title']}</h2>
                        
                        <div style="color: #4a5568; font-size: 16px; margin-bottom: 24px; white-space: pre-wrap;">{content['description']}</div>
                        
                        <!-- Verse Callout -->
                        <div style="background-color: #fffaf0; padding: 24px; border-left: 4px solid #ed8936; margin: 32px 0; border-radius: 4px;">
                            <p style="font-style: italic; margin: 0; color: #2d3748; font-size: 18px; line-height: 1.6;">{content['verse']}</p>
                        </div>

                        <div style="color: #4a5568; font-size: 16px; margin-bottom: 32px; white-space: pre-wrap;">{content.get('outro', '')}</div>

                        <!-- Reflection Section -->
                        <div style="margin-top: 40px; padding: 24px; background-color: #ebf8ff; border-radius: 12px;">
                            <h4 style="margin-top: 0; color: #2b6cb0; text-transform: uppercase; font-size: 13px; letter-spacing: 0.05em;">Take a moment to reflect</h4>
                            <p style="margin-bottom: 0; color: #2c5282; font-size: 16px;">{content.get('reflection', '')}</p>
                        </div>

                        <!-- Prayer Section -->
                        <div style="margin-top: 24px; padding: 24px; background-color: #f0fff4; border-radius: 12px;">
                            <h4 style="margin-top: 0; color: #2f855a; text-transform: uppercase; font-size: 13px; letter-spacing: 0.05em;">Simple Prayer</h4>
                            <p style="margin-bottom: 0; color: #276749; font-size: 16px; font-style: italic;">{content.get('prayer', '')}</p>
                        </div>

                        <div style="margin-top: 48px; border-top: 1px solid #edf2f7; padding-top: 32px;">
                            <p style="margin-bottom: 4px; color: #4a5568;">{content.get('sign_off', 'Hope begins here,')}</p>
                            <p style="margin-top: 0; font-weight: 700; color: #2d3748;">HopeBegins Team</p>
                        </div>

                        <div style="margin-top: 32px; font-size: 13px; color: #a0aec0;">
                            <p style="margin-bottom: 8px;">More from HopeBegins:</p>
                            <div style="display: flex; flex-direction: column; gap: 8px;">
                                <a href="https://hopebegins.today/give-hope" style="color: #ed8936; text-decoration: none;">• Support HopeBegins</a>
                                <a href="https://hopebegins.today/prayers" style="color: #ed8936; text-decoration: none;">• Share your prayer requests</a>
                            </div>
                        </div>
                    </div>

                    {visit_site_html('/')}

                    <div style="background-color: #edf2f7; padding: 24px; text-align: center; font-size: 12px; color: #718096;">
                        <p style="margin: 0;">You are receiving this because you signed up for the 21-day Hope Journey.</p>
                    </div>
                </div>
            </body>
        </html>
        """
        
    from django.conf import settings
    from_email = settings.DEFAULT_FROM_EMAIL
    to = subscriber.email

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    
    try:
        logger.info(f"Attempting to send Daily Hope email (Day {day}) to {subscriber.email}")
        msg.send()
        logger.info(f"Successfully sent Daily Hope email (Day {day}) to {subscriber.email}")
        
        # Increment day or finish AFTER successful send
        if day >= 21:
            logger.info(f"Subscriber {subscriber.email} completed the 21-day journey")
            subscriber.is_active = False
            subscriber.finished_at = timezone.now()
        else:
            subscriber.current_day += 1
        
        subscriber.save()
        return True
        
    except Exception as e:
        # Log error
        logger.error(f"Error sending Daily Hope email to {subscriber.email}: {e}", exc_info=True)
        return False

@shared_task
def send_daily_hope_emails():
    logger.info("Task send_daily_hope_emails triggered")
    # Find all active subscribers
    active_subscribers = HopeJourney.objects.filter(is_active=True)
    
    logger.info(f"Found {active_subscribers.count()} active subscribers for Daily Hope emails")
    for subscriber in active_subscribers:
        send_subscriber_email_logic(subscriber)

@shared_task
def send_welcome_and_day_one(subscriber_id):
    """
    Called immediately upon signup.
    Sends Day 1 email and sets subscriber ready for Day 2 on next schedule.
    """
    logger.info(f"Task send_welcome_and_day_one triggered for subscriber_id={subscriber_id}")
    try:
        subscriber = HopeJourney.objects.get(id=subscriber_id)
        if subscriber.current_day == 1:
            send_subscriber_email_logic(subscriber)
            logger.info(f"Processed Day 1 email for subscriber_id={subscriber_id}")
    except HopeJourney.DoesNotExist:
        logger.warning(f"Subscriber with id={subscriber_id} does not exist. Cannot send Day 1 email.")
        pass
