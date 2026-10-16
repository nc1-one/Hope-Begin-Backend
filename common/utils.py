import logging
import time
from html import escape

from django.conf import settings
from django.core.mail import EmailMultiAlternatives

logger = logging.getLogger(__name__)

def validate_form_time(start_time_ms, min_seconds=3):
    """
    Validates that the form took at least min_seconds to submit.
    start_time_ms is the timestamp from the frontend in milliseconds.
    """
    if not start_time_ms:
        return False
        
    try:
        start_time = int(start_time_ms) / 1000.0
        current_time = time.time()
        duration = current_time - start_time
        
        # If duration is negative (clock skew) or too short, it's likely a bot
        if duration < min_seconds or duration > 3600: # Max 1 hour
            return False
        return True
    except (ValueError, TypeError):
        return False

def check_spam_keywords(text):
    """
    Checks if the text contains common spam/phishing keywords.
    """
    if not text:
        return False
        
    spam_keywords = [
        'crypto', 'bitcoin', 'ethereum', 'seo', 'marketing', 
        'click here', 'buy now', 'money back', 'win prize',
        'casino', 'porn', 'cheap', 'discount', 'viagra'
    ]
    
    text_lower = text.lower()
    for keyword in spam_keywords:
        if keyword in text_lower:
            return True
    return False


def get_site_url(path="/"):
    base_url = getattr(settings, "FRONTEND_URL", "https://hopebegins.today").rstrip("/")
    clean_path = path if path.startswith("/") else f"/{path}"
    return f"{base_url}{clean_path}"


def append_visit_site_text(message, path="/", button_label=None):
    site_url = get_site_url(path)
    if button_label:
        return f"{message.rstrip()}\n\n{button_label}: {site_url}"
    return (
        f"{message.rstrip()}\n\n"
        "Need more encouragement or want to return to HopeBegins?\n"
        f"Visit HopeBegins: {site_url}"
    )


def visit_site_html(path="/", label="Visit HopeBegins"):
    site_url = get_site_url(path)
    return f"""
    <div style="margin: 32px 0; text-align: center;">
        <a href="{site_url}" style="display: inline-block; background-color: #a3b18a; color: #ffffff; padding: 14px 24px; border-radius: 999px; text-decoration: none; font-weight: 700; font-family: Arial, sans-serif;">
            {escape(label)}
        </a>
        <p style="margin: 12px 0 0; color: #6b7280; font-size: 13px; font-family: Arial, sans-serif;">
            Or open this link: <a href="{site_url}" style="color: #6b634d;">{site_url}</a>
        </p>
    </div>
    """


def append_visit_site_html(html_content, path="/"):
    if "Visit HopeBegins" in html_content:
        return html_content
    return f"{html_content}{visit_site_html(path)}"


def plain_text_to_html(message, path="/", button_label=None):
    escaped_message = escape(message).replace("\n", "<br>")
    return f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #222222; line-height: 1.6; background-color: #f7f7f2; padding: 24px;">
            <div style="max-width: 640px; margin: 0 auto; background-color: #ffffff; border-radius: 18px; padding: 32px; border: 1px solid #ece9dd;">
                <div style="font-size: 15px;">{escaped_message}</div>
                {visit_site_html(path, button_label or "Visit HopeBegins")}
            </div>
        </body>
    </html>
    """


def send_notification_email(subject, message, recipient_list, path="/", button_label=None):
    text_content = append_visit_site_text(message, path, button_label)
    html_content = plain_text_to_html(message, path, button_label)
    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
    )
    email.attach_alternative(html_content, "text/html")
    return email.send(fail_silently=False)
