import logging
from html import escape

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from django.utils import timezone

from common.email_copy import colon, copy_for, site_path
from common.email_parts import BORDER, BROWN, SAGE_LIGHT, TEAL, button_html, crisis_html, crisis_text, page_html
from common.utils import append_visit_site_html, append_visit_site_text, get_site_url

from .journey import IMAGES, LAST_DAY, day_in
from .models import EmailTemplate, HopeJourney

logger = logging.getLogger(__name__)


def stop_url(subscriber):
    """The page that stops a subscriber's emails, on the API's own address."""
    return settings.API_URL.rstrip('/') + reverse('daily-hope-stop', args=[subscriber.id])


def _paragraphs(text):
    return ''.join(
        f'<p style="margin: 0 0 14px;">{escape(part)}</p>'
        for part in text.split('\n\n')
        if part.strip()
    )


def build_day_email(subscriber, day):
    """Subject, plain text and HTML for one day, or None past the last day."""
    lang = subscriber.lang
    content = day_in(lang, day)
    if content is None:
        return None
    c = copy_for(lang).DAILY
    name = subscriber.first_name.strip()
    greeting = c['greeting'].format(name=name) if name else ''
    subject = c['subject'].format(day=day, title=content['title'])
    home = get_site_url(site_path(lang, '/'))
    prayers = get_site_url(site_path(lang, '/prayers'))
    give = get_site_url(site_path(lang, '/give-hope'))
    stop = stop_url(subscriber)

    html = page_html(f"""
                <img src="{escape(IMAGES[day], quote=True)}" alt="" width="576" style="display: block; width: 100%; height: auto; border-radius: 14px;">
                <p style="margin: 24px 0 0; font-size: 13px; font-weight: 700; color: {TEAL};">{escape(c['day_label'].format(day=day))}</p>
                <h1 style="font-family: Georgia, 'Times New Roman', serif; font-weight: 400; font-size: 32px; line-height: 1.15; margin: 6px 0 20px;">{escape(content['title'])}</h1>
                {f'<p style="margin: 0 0 14px;">{escape(greeting)}</p>' if greeting else ''}
                {_paragraphs(content['opening'])}
                <div style="margin: 24px 0; background-color: {SAGE_LIGHT}; border-radius: 14px; padding: 20px 22px;">
                    <p style="margin: 0; font-family: Georgia, 'Times New Roman', serif; font-size: 19px; line-height: 1.5;">{escape(content['verse'])}</p>
                    <p style="margin: 10px 0 0; font-size: 14px; font-weight: 700;">{escape(content['verse_ref'])}</p>
                </div>
                {_paragraphs(content['after'])}
                <div style="margin-top: 24px; border: 1px solid {BORDER}; border-radius: 14px; padding: 18px 20px;">
                    <p style="margin: 0; font-weight: 700;">{escape(c['reflect_label'])}</p>
                    <p style="margin: 6px 0 0;">{escape(content['question'])}</p>
                </div>
                <div style="margin-top: 12px; border: 1px solid {BORDER}; border-radius: 14px; padding: 18px 20px;">
                    <p style="margin: 0; font-weight: 700;">{escape(c['prayer_label'])}</p>
                    <p style="margin: 6px 0 0; font-style: italic;">{escape(content['prayer'])}</p>
                </div>
                <p style="margin: 28px 0 0;">{escape(c['team'])}</p>

                {button_html(home, c['visit'], c['or_open_link'])}

                <p style="margin: 0; font-size: 14px;"><a href="{prayers}" style="color: {BROWN}; font-weight: 700;">{escape(c['prayers_link'])}</a> · <a href="{give}" style="color: {BROWN}; font-weight: 700;">{escape(c['support_link'])}</a></p>

                {crisis_html(lang, subscriber.country)}

                <p style="margin: 28px 0 0; font-size: 12px; color: {TEAL};">{escape(c['footer'])} <a href="{stop}" style="color: {TEAL};">{escape(c['stop'])}</a></p>
    """, lang)

    text = '\n'.join(filter(lambda line: line is not None, [
        c['day_label'].format(day=day),
        content['title'],
        '',
        greeting or None,
        '' if greeting else None,
        content['opening'],
        '',
        content['verse'],
        content['verse_ref'],
        '',
        content['after'],
        '',
        f"{c['reflect_label']}{colon(lang)}{content['question']}",
        '',
        f"{c['prayer_label']}{colon(lang)}{content['prayer']}",
        '',
        c['team'],
        '',
        f"{c['visit']}{colon(lang)}{home}",
        f"{c['prayers_link']}{colon(lang)}{prayers}",
        f"{c['support_link']}{colon(lang)}{give}",
        '',
        crisis_text(lang, subscriber.country),
        '',
        c['footer'],
        f"{c['stop']}{colon(lang)}{stop}",
    ]))
    return subject, text, html


def _dashboard_template(subscriber, day):
    """An English day written in the admin dashboard takes the place of the built-in one."""
    if subscriber.lang != 'en':
        return None
    template = EmailTemplate.objects.filter(day_number=day, is_active=True).first()
    if template is None:
        return None
    c = copy_for('en').DAILY
    stop = stop_url(subscriber)
    html = append_visit_site_html(template.html_content)
    text = append_visit_site_text(c['template_text'].format(day=day))
    html = html.replace('</body>', f'<p style="font-size: 12px;"><a href="{stop}">{escape(c["stop"])}</a></p></body>', 1)
    return template.subject, f"{text}\n\n{c['stop']}{colon('en')}{stop}", html


def send_subscriber_email_logic(subscriber):
    """
    Sends a subscriber the day they are on and moves them to the next one.
    After the last day they are marked finished.
    """
    day = subscriber.current_day
    logger.info('Processing Daily Hope day %s for subscriber %s', day, subscriber.id)

    built = _dashboard_template(subscriber, day) or build_day_email(subscriber, day)
    if built is None:
        if day > LAST_DAY:
            subscriber.is_active = False
            subscriber.finished_at = timezone.now()
            subscriber.save()
        return False
    subject, text, html = built

    stop = stop_url(subscriber)
    message = EmailMultiAlternatives(
        subject,
        text,
        settings.DEFAULT_FROM_EMAIL,
        [subscriber.email],
        # One-tap unsubscribe in mail apps that support it.
        headers={
            'List-Unsubscribe': f'<{stop}>',
            'List-Unsubscribe-Post': 'List-Unsubscribe=One-Click',
        },
    )
    message.attach_alternative(html, 'text/html')

    try:
        message.send()
    except Exception:
        logger.exception('Failed to send Daily Hope day %s to subscriber %s', day, subscriber.id)
        return False

    if day >= LAST_DAY:
        subscriber.is_active = False
        subscriber.finished_at = timezone.now()
    else:
        subscriber.current_day += 1
    subscriber.save()
    return True


@shared_task
def send_daily_hope_emails():
    for subscriber in HopeJourney.objects.filter(is_active=True):
        send_subscriber_email_logic(subscriber)


@shared_task
def send_welcome_and_day_one(subscriber_id):
    """Sends Day 1 right after signing up; the daily task sends the rest."""
    try:
        subscriber = HopeJourney.objects.get(id=subscriber_id)
    except HopeJourney.DoesNotExist:
        logger.warning('Daily Hope subscriber %s no longer exists', subscriber_id)
        return
    if subscriber.current_day == 1:
        send_subscriber_email_logic(subscriber)
