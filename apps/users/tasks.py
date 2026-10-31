from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from html import escape

from django.core.mail import EmailMultiAlternatives

from common.email_copy import colon, copy_for, site_path
from common.email_parts import button_html, page_html
from common.utils import get_site_url, send_notification_email
import logging

logger = logging.getLogger(__name__)

User = get_user_model()

@shared_task
def send_approval_email(user_id, temp_password):
    logger.info(f"Task send_approval_email triggered for user_id={user_id}")
    try:
        user = User.objects.get(id=user_id)
        login_url = f"{settings.FRONTEND_URL}/login/carrier"
        
        subject = "You're now a Hope Carrier"
        message = (
            f"Your application to be a Hope Carrier has been approved.\n\n"
            f"You can log in to your dashboard with these details:\n"
            f"Username: {user.email}\n"
            f"Temporary password: {temp_password}\n\n"
            f"Log in here: {login_url}\n\n"
            "Please change your password the first time you log in.\n\n"
            "Thank you for praying for people who are hurting."
        )
        
        logger.info(f"Attempting to send approval email to {user.email}")
        send_notification_email(
            subject,
            message,
            [user.email],
            path="/login/carrier",
        )
        logger.info(f"Successfully sent approval email to {user.email}")
        return f"Approval email sent to {user.email}"
    except User.DoesNotExist:
        logger.warning(f"Failed to send approval email: User with ID {user_id} does not exist")
        return f"User with ID {user_id} does not exist"
    except Exception as e:
        logger.error(f"Error sending approval email to user_id={user_id}: {str(e)}", exc_info=True)
        return f"Error sending approval email: {str(e)}"

@shared_task
def send_password_reset_email(email, reset_url):
    logger.info(f"Task send_password_reset_email triggered for email={email}")
    try:
        logger.info(f"Attempting to send password reset email to {email}")
        send_notification_email(
            "Reset your HopeBegins password",
            f"Use this link to reset your password: {reset_url}\n\n"
            "If you didn't ask to reset it, you can ignore this email.",
            [email],
            path="/",
        )
        logger.info(f"Successfully sent password reset email to {email}")
        return f"Password reset email sent to {email}"
    except Exception as e:
        logger.error(f"Error sending password reset email to {email}: {str(e)}", exc_info=True)
        return f"Error sending password reset email: {str(e)}"

@shared_task
def send_prayer_encouragement_email(to_email, subject, message, lang='en'):
    """The "a Hope Carrier prayed for you" email, in the language they asked in."""
    logger.info("Task send_prayer_encouragement_email triggered")
    c = copy_for(lang).DAILY
    url = get_site_url(site_path(lang, '/'))
    text = f"{message}\n\n{c['visit']}{colon(lang)}{url}"
    html = page_html(
        f'<div style="font-size: 15px;">{escape(message).replace(chr(10), "<br>")}</div>'
        + button_html(url, c['visit'], c['or_open_link']),
        lang,
    )
    try:
        email = EmailMultiAlternatives(subject, text, settings.DEFAULT_FROM_EMAIL, [to_email])
        email.attach_alternative(html, 'text/html')
        email.send(fail_silently=False)
        return 'Encouragement email sent'
    except Exception as e:
        logger.error(f"Error sending encouragement email: {str(e)}", exc_info=True)
        return f"Error sending encouragement email: {str(e)}"

@shared_task
def send_assignment_notification_email(carrier_email, prayer_title=None):
    # The requester's name never goes in the email, even if they shared it:
    # they may have asked to stay anonymous, and the dashboard respects that.
    # prayer_title stays as a parameter for tasks already in the queue.
    logger.info(f"Task send_assignment_notification_email triggered for carrier_email={carrier_email}")
    try:
        login_url = f"{settings.FRONTEND_URL}/login/carrier"
        subject = "A new prayer request for you"
        message = (
            f"Hi,\n\n"
            f"A prayer request is waiting for you.\n\n"
            f"Please log in to your dashboard to read it and pray:\n"
            f"{login_url}\n\n"
            "Thank you for praying."
        )
        
        send_notification_email(
            subject,
            message,
            [carrier_email],
            path="/login/carrier",
        )
        logger.info(f"Successfully sent assignment email to {carrier_email}")
        return f"Assignment email sent to {carrier_email}"
    except Exception as e:
        logger.error(f"Error sending assignment email to {carrier_email}: {str(e)}", exc_info=True)
        return f"Error sending assignment email: {str(e)}"

@shared_task
def send_admin_invite_email(user_id, invited_by):
    """Invite a new admin to set their password and sign in."""
    try:
        user = User.objects.get(id=user_id)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        days = settings.PASSWORD_RESET_TIMEOUT // 86400
        name = user.first_name or "there"
        message = (
            f"Hi {name},\n\n"
            f"{invited_by} added you as an admin on HopeBegins.\n\n"
            f"Set your password with the link below. It works for {days} days. "
            f"If it runs out, ask {invited_by} to send a new one.\n\n"
            f"After that, sign in at {settings.FRONTEND_URL}/admin/login with this email address.\n\n"
            "Prayer requests in the admin panel are private. Please keep what you read there to yourself."
        )
        send_notification_email(
            "HopeBegins: you've been added as an admin",
            message,
            [user.email],
            path=f"/reset-password?uid={uid}&token={token}&for=admin",
            button_label="Set your password",
        )
        logger.info(f"Admin invite sent to user_id={user_id}")
        return f"Admin invite sent to {user.email}"
    except User.DoesNotExist:
        logger.warning(f"Admin invite skipped: user_id={user_id} does not exist")
        return f"User with ID {user_id} does not exist"
    except Exception as e:
        logger.error(f"Error sending admin invite to user_id={user_id}: {str(e)}", exc_info=True)
        return f"Error sending admin invite: {str(e)}"
